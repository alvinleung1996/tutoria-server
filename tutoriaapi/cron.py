from django_cron import CronJobBase, Schedule
from .models import *
from datetime import datetime, timezone

class cronJob(CronJobBase):
    RUN_EVERY_MINS = 30 # every 30 minutes

    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'cron.cron_job'    # a unique code

    def do(self):
        print("Locking all sessions")
        for tutorial in Tutorial.objects.filter(cancelled=False).filter(start_time__lte=datetime.now(tz=timezone.utc)):
            print(tutorial.start_time)
            print(tutorial.end_time)
        print("Locked all sessions")
        print("Ending all sessions")
        for tutorial in Tutorial.objects.filter(end_time__lte=datetime.now(tz=timezone.utc)).filter(company_to_tutor_transaction__isnull=True):
            print(tutorial.start_time)
            print(tutorial.end_time)
            tutorial.pay_to_tutor()
        print("Ended all sessions")