from django.db import models
from .occupiedsessions import TutorialSession

class Review(models.Model):

    @classmethod
    def create(cls, tutorialSession, comment, creationTime, anonymous=False):
        return cls.objects.create(
            tutorialSession = tutorialSession,
            anonymous = anonymous,
            comment = comment,
            creationTime = creationTime
        )


    tutorialSession = models.OneToOneField(TutorialSession, on_delete=models.PROTECT, related_name='review', related_query_name='review')

    comment = models.TextField()
    ratingScore = models.IntegerField(default=5)
    creationTime = models.DateTimeField()
    anonymous = models.BooleanField(default=False)

    def __str__(self):
        return 'Review: '.format(self=self)
