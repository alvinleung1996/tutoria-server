from django.db import models

from . import user

class Event(models.Model):

    user_set = models.ManyToManyField('User', related_name='event_set', related_query_name='event')

    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
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
