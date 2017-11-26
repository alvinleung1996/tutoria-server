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
    1. Search for tutor
    2. Select tutor
    3. Select timeslot
    4. Confirm booking and payment
### 2. Cancel Session
    1. Select booked session
    2. Confirm cancellation
### 3. Lock All Sessions
This is not implemented by the scheduler but only done by checking conditions.

### 4. End All Sessions
#### Cron
A cron file is created to manually End All Sessions that have passed(instead of using scheduler), which can be run by this command: 
```
$ python manage.py runcrons --force
```
    1. System searches for all passed sessions not ended
    2. System performs payment(if needed)
    3. System sends invitation to review messages to corresponding students
    4. System marks all those sessions as ended
## Database
SQLite in django has been used

## Extra
### Email
Console log message is used to simulate email
