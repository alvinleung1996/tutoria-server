from datetime import datetime, timezone

from django.db import models

class Coupon(models.Model):

    @classmethod
    def create(cls, code, start_time, end_time):
        if start_time is None:
            start_time = datetime.now(tz=timezone.utc)
        return cls.objects.create(
            code = code,
            start_time = start_time,
            end_time = end_time
        )

    code = models.CharField(max_length=16)

    start_time = models.DateTimeField()

    end_time = models.DateTimeField()
