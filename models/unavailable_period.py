from django.db import models

# from .tutor import Tutor
# cyclic dependencies

from . import event

class UnavailablePeriod(event.Event):

    @classmethod
    def create(cls, tutor, start_time, end_time, cancelled=False):
        period = cls.objects.create(
            start_time = start_time,
            end_time = end_time,
            cancelled = cancelled,
            tutor = tutor
        )
        period.user_set = [tutor.user]
        return period


    event = models.OneToOneField('Event', on_delete=models.CASCADE, parent_link=True, related_name='unavailable_period', related_query_name='unavailable_period')

    tutor = models.ForeignKey('Tutor', on_delete=models.CASCADE, related_name='unavailable_period_set', related_query_name='unavailable_period_set')

    def __str__(self):
        return 'UnavailablePeriod: {self.start_time} - {self.end_time} : {self.tutor}'.format(self=self)
