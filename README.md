Smart Med Django Application

To run the application locally you will these installed so if you don't install from the python website:
. Python 3.7 and above
. PIP

Extract the file 

Open and IDE like VsCode

Navigate to extracted folder and open 

Open a new terminal in IDE

Navigate to SmartMed folder using cd

Install all dependencies using the command below:
pip install -r requirements.txt

Apply migrations using command:
python manage.py migrate

Run the application using command:
python manage.py runserver

Visit http://127.0.0.1:8000/ in your browser
