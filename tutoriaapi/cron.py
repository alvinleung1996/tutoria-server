from django_cron import CronJobBase, Schedule
from decimal import Decimal
from .models import *
from datetime import datetime, timezone

class cronJob(CronJobBase):
    RUN_EVERY_MINS = 30 # every 30 minutes

    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'cron.cron_job'    # a unique code

    def do(self):
        print("Locking all sessions")
        for tutorial in Tutorial.objects.filter(
                cancelled=False,
                start_time__lte=datetime.now(tz=timezone.utc),
                company_to_tutor_transaction__isnull=True
            ):
            print(tutorial.start_time)
            print(tutorial.end_time)
        print("Locked all sessions")
        print("Ending all sessions")
        for tutorial in Tutorial.objects.filter(
            cancelled=False, 
            tutor_fee__gt=Decimal('0'),
            end_time__lte=datetime.now(tz=timezone.utc),
            company_to_tutor_transaction__isnull=True
        ):
            print(tutorial.start_time)
            print(tutorial.end_time)
            tutorial.pay_to_tutor()
            self.invitationToReview(tutorial)
        print("Ended all sessions")
    
    def invitationToReview(self, tutorial):
        content = ('You are invited to review the tutorial you have attended: '
                + '/tutorials/' + tutorial.pk + '/review')
        message.Message.create(
            send_user = user.User.objects.get(company__isnull=False),
            receive_user = tutorial.student.user,
            title = 'Tutorial review',
            content = content
        )
        print('Invitation to review sent to ' + tutorial.student.user.username)