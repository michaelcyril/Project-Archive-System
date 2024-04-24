# pams
# project archives management system
Download the Project 
Install all project dependencies using the requirements.txt file using the command
pip install -r requirements.txt

check on settings.py file and update the database part with your credentials

create database

migrate the table using the commang 
python manage.py migrate


crete superuser
python manage.py createsuperuser

load seeders
python manage.py loaddata seeders.json

run the server
python manage.py runserver


NB
The system contain Three kind of users 
1.Admin
2.Coordinator
3.Student

