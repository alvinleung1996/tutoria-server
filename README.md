# tutoria-server
## Basics
1. Download Python3.6 from [Python Downloads](https://www.python.org/downloads/)
2. Open Terminal and install django by running: ```pip install -e django/```
3. Navigate to the project directory, starts the server by running: ```python3.6 manage.pyunserver```
4. Open a web browser, and go to the link to as shown in the console log

## Major Use Case
### Book Session

### Cancel Session

### End All Sessions
Scheduler is not implemented because it is OS-specific. A cron file is created to manually End All Sessions that have passed, which can be run by this command: 
```python manage.py runcrons --force```

### User

### Tutor

### Student

### Wallet

### Email
Console log message is used to simulate email.
