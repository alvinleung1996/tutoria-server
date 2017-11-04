from datetime import datetime, timezone

from django.db import models

class Review(models.Model):

    @classmethod
    def create(cls, tutorial, comment, time=None, anonymous=False):
        if time is None:
            time = datetime.now(tz=timezone.utc)
        return cls.objects.create(
            tutorial = tutorial,
            anonymous = anonymous,
            comment = comment,
            time = time
        )


    tutorial = models.OneToOneField('Tutorial', on_delete=models.CASCADE, related_name='review', related_query_name='review')

    comment = models.TextField()
    score = models.IntegerField(default=5)
    time = models.DateTimeField()
    anonymous = models.BooleanField(default=False)

    def __str__(self):
        return 'Review: '.format(self=self)
