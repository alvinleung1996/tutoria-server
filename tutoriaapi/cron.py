from django_cron import CronJobBase, Schedule
from .models import *
from datetime import datetime, timezone

class cronJob(CronJobBase):
    RUN_EVERY_MINS = 30 # every 30 minutes

    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'cron.cron_job'    # a unique code

    def do(self):
        print(User.objects.all().count())
        for tutorial in Tutorial.objects.all():
            print(tutorial.start_time)
            print(tutorial.end_time)
            print(datetime.now(tz=timezone.utc))
            print(datetime.now(tz=timezone.utc) > tutorial.start_time)
            