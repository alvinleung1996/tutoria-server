# tutoria-server
## Basics
1. Download Python3.6 from [Python Downloads](https://www.python.org/downloads/)
2. Open Terminal and install django by running: ```$ python3.6 -m pip install -e django/```
3. To install the datautil package used in this project, run this command: ```$ python3.6 -m pip install python-dateutil```
4. To install the crontab package used in this project, run this command: ```$ python3.6 -m pip install django-cron```
5. Navigate to the project directory and start the server by running: ```$ python3.6 manage.py runserver```
6. Open a web browser and go to the link as shown in the console log

## Major Use Cases
### 1. Book Session

### 2. Cancel Session

### 3. Lock All Sessions
This is not implemented by the scheduler.

### 4. End All Sessions
Scheduler is not implemented because it is OS-specific. A cron file is created to manually End All Sessions that have passed, which can be run by this command: 
```
$ python manage.py runcrons --force
```

## Database
SQLite in django has been used

## Extra
### Email
Console log message is used to simulate email
