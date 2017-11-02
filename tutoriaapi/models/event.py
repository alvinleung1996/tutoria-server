from django.db import models
from .user import User
# from . import roles # cyclic dependencies


class Event(models.Model):

    user_set = models.ManyToManyField(User, related_name='event_set', related_query_name='event_set')

    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    cancelled = models.BooleanField(default=False)

    @property
    def concrete_event(self):
        if hasattr(self, 'tutorial'):
            return self.tutorial
        elif hasattr(self, 'unavailable_period'):
            return self.unavailable_period
        else:
            return None

    def __str__(self):
        concrete_event = self.concrete_event
        return 'Event <abstract>: ' + (concrete_event.__str__() if (concrete_event is not None) else 'Unknown!')



class Tutorial(Event):

    @classmethod
    def create(cls, student, tutor, start_date, end_date, cancelled=False, locked=False):
        tutorial = cls.objects.create(
            startDate = startDate,
            end_date = end_date,
            cancelled = cancelled,
            student = student,
            tutor = tutor,
            locked = locked
        )
        tutorial.user_set = [student.user, tutor.user]
        return tutorial

    event = models.OneToOneField(Event, on_delete=models.CASCADE, parent_link=True, related_name='tutorial', related_query_name='tutorial')
    
    student = models.ForeignKey('Student', on_delete=models.PROTECT, related_name='tutorial_set', related_query_name='tutorial_set')
    tutor = models.ForeignKey('Tutor', on_delete=models.PROTECT, related_name='tutorial_set', related_query_name='tutorial_set')
    locked = models.BooleanField(default=False)

    def __str__(self):
        return 'Tutorial: {self.locked}'.format(self=self)



class UnavailablePeriod(Event):

    @classmethod
    def create(cls, tutor, start_date, end_date, cancelled=False):
        period = cls.objects.create(
            start_date = start_date,
            end_date = end_date,
            cancelled = cancelled,
            tutor = tutor
        )
        period.user_set = [tutor.user]
        return period


    event = models.OneToOneField(Event, on_delete=models.CASCADE, parent_link=True, related_name='unavailable_period', related_query_name='unavailable_period')

    tutor = models.ForeignKey('Tutor', on_delete=models.CASCADE, related_name='unavailable_period_set', related_query_name='unavailable_period_set')

    def __str__(self):
        return 'UnavailablePeriod: {self.start_date} - {self.end_date} : {self.tutor}'.format(self=self)
