# tutoria-server
## Basics
1. Download Python3.6 from [Python Downloads](https://www.python.org/downloads/)
2. Open Terminal and install django by running: ```pip install -e django/```
3. To install the datautil package used in this project, run this command: ```pip install python-dateutil```
4. To install the crontab package used in this project, run this command: ```pip install django-crontab```
5. Navigate to the project directory and start the server by running: ```python3.6 manage.py runserver```
6. Open a web browser and go to the link to as shown in the console log

## Major Use Cases
### Book Session

### Cancel Session

### End All Sessions
Scheduler is not implemented because it is OS-specific. A cron file is created to manually End All Sessions that have passed, which can be run by this command: 
```python manage.py runcrons --force```

## Database
SQLite in django has been used

#### Email
Console log message is used to simulate email
