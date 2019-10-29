from datetime import datetime

from django.db import models
from django.utils import timezone as djtimezone

class Coupon(models.Model):

    @classmethod
    def create(cls, code, start_time, end_time):
        if start_time is None:
            start_time = datetime.now(tz=djtimezone.get_default_timezone())

        return cls.objects.create(
            code = code,
            start_time = start_time,
            end_time = end_time
        )

    code = models.CharField(max_length=16)

    start_time = models.DateTimeField()

    end_time = models.DateTimeField()

    def is_valid_now(self):
        current_time = datetime.now(tz=djtimezone.get_default_timezone())
        return self.start_time <= current_time and self.end_time > current_time
