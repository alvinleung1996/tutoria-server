from django.db import models
from .user import User
# from . import roles cyclic dependencies


class Event(models.Model):

    userSet = models.ManyToManyField(User, related_name='eventSet', related_query_name='eventSet')

    startDate = models.DateTimeField()
    endDate = models.DateTimeField()
    cancelled = models.BooleanField(default=False)

    @property
    def concreteEvent(self):
        if hasattr(self, 'tutorial'):
            return self.tutorial
        elif hasattr(self, 'unavailablePeriod'):
            return self.unavailablePeriod
        else:
            return None

    def __str__(self):
        concreteEvent = self.concreteEvent
        return 'Event <abstract>: ' + (concreteEvent.__str__() if (concreteEvent is not None) else 'Unknown!')



class Tutorial(Event):

    @classmethod
    def create(cls, student, tutor, startDate, endDate, cancelled=False, locked=False):
        tutorial = cls.objects.create(
            startDate = startDate,
            endDate = endDate,
            cancelled = cancelled,
            student = student,
            tutor = tutor,
            locked = locked
        )
        tutorial.userSet = [student.user, tutor.user]
        return tutorial

    event = models.OneToOneField(Event, on_delete=models.CASCADE, parent_link=True, related_name='tutorial', related_query_name='tutorial')
    
    student = models.ForeignKey('Student', on_delete=models.PROTECT, related_name='tutorialSet', related_query_name='tutorialSet')
    tutor = models.ForeignKey('Tutor', on_delete=models.PROTECT, related_name='tutorialSet', related_query_name='tutorialSet')
    locked = models.BooleanField(default=False)

    def __str__(self):
        return 'Tutorial: {self.locked}'.format(self=self)



class UnavailablePeriod(Event):

    @classmethod
    def create(cls, tutor, startDate, endDate, cancelled=False):
        period = cls.objects.create(
            startDate = startDate,
            endDate = endDate,
            cancelled = cancelled,
            tutor = tutor
        )
        period.userSet = [tutor.user]
        return period


    event = models.OneToOneField(Event, on_delete=models.CASCADE, parent_link=True, related_name='unavailablePeriod', related_query_name='unavailablePeriod')

    tutor = models.ForeignKey('Tutor', on_delete=models.CASCADE, related_name='unavailablePeriodSet', related_query_name='unavailablePeriodSet')

    def __str__(self):
        return 'UnavailablePeriod: {self.startDate} - {self.endDate} : {self.tutor}'.format(self=self)
