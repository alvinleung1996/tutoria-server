from django.db import models
from .event import Tutorial

class Review(models.Model):

    @classmethod
    def create(cls, tutorial, comment, creationDate, anonymous=False):
        return cls.objects.create(
            tutorial = tutorial,
            anonymous = anonymous,
            comment = comment,
            creationDate = creationDate
        )


    tutorial = models.OneToOneField(Tutorial, on_delete=models.CASCADE, related_name='review', related_query_name='review')

    comment = models.TextField()
    score = models.IntegerField(default=5)
    creationDate = models.DateTimeField()
    anonymous = models.BooleanField(default=False)

    def __str__(self):
        return 'Review: '.format(self=self)
