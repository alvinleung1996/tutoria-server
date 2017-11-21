from django.utils import timezone as djtimezone

from datetime import datetime

from django.db import models

class Review(models.Model):

    @classmethod
    def create(cls, tutorial, comment, score, time=None, anonymous=False, **kwargs):
        if time is None:
            time = datetime.now(tz=djtimezone.get_default_timezone())
        return cls.objects.create(
            tutorial = tutorial,
            comment = comment,
            score = score,
            time = time,
            anonymous = anonymous,
        )


    tutorial = models.OneToOneField('Tutorial', on_delete=models.CASCADE, related_name='review', related_query_name='review')

    comment = models.TextField()
    score = models.IntegerField(default=5)
    time = models.DateTimeField()
    anonymous = models.BooleanField(default=False)

    def __str__(self):
        return 'Review: {self.score}'.format(self=self)
