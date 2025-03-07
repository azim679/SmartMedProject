import json
from channels.generic.websocket import AsyncWebsocketConsumer

#uses django channels to handle video call signalling with websocket consumer 
class VideoCallConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        #gets room name from url pattern 
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f"call_{self.room_name}"
        self.user = self.scope["user"]

        #understands the role of the user or doctor in call
        is_doctor = hasattr(self.user, 'doctor') 
        if is_doctor:
            self.role = "callee"  # Doctors wait for the offer
        else:
            self.role = "caller"  # Patients create the offer

        #tracks active users in the room and creates dictionary if it doesnt exist
        if not hasattr(self.channel_layer, "active_rooms"):
            self.channel_layer.active_rooms = {}

        if self.room_group_name not in self.channel_layer.active_rooms:
            self.channel_layer.active_rooms[self.room_group_name] = []

        #adds user to active room list
        self.channel_layer.active_rooms[self.room_group_name].append(self.channel_name)

        #join the  websocket group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

        #send roles to the client
        await self.send(json.dumps({
            "type": "role",
            "role": self.role
        }))

        #let others know when a new user joins
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "user.joined",
                "sender": self.channel_name,
                "user_id": self.user.id,
                "role": self.role,
            }
        )

    #delete room if no one left and remove user from active room list
    async def disconnect(self, close_code):
        if self.room_group_name in self.channel_layer.active_rooms:
            self.channel_layer.active_rooms[self.room_group_name].remove(self.channel_name)

            if not self.channel_layer.active_rooms[self.room_group_name]:
                del self.channel_layer.active_rooms[self.room_group_name]

        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    #handles incoming messages
    async def receive(self, text_data):
        data = json.loads(text_data)
        data["sender"] = self.user.id

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "relay.message",
                "data": data,
                "sender": self.channel_name
            }
        )

    #relays messages to others
    async def relay_message(self, event):
        if self.channel_name != event["sender"]:
            await self.send(text_data=json.dumps(event["data"]))

    #offer created if caller and another user joins
    async def user_joined(self, event):
        if self.role == "caller" and event["sender"] != self.channel_name:
            await self.send(json.dumps({"type": "request_offer"}))