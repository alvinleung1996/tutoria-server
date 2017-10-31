from django.db import models
from .userprofile import UserProfile
# from . import roles cyclic dependencies


class OccupiedSession(models.Model):

    userProfileSet = models.ManyToManyField(UserProfile, related_name='occupiedSessionSet', related_query_name='occupiedSessionSet')

    startDate = models.DateTimeField()
    endDate = models.DateTimeField()
    cancelled = models.BooleanField(default=False)

    @property
    def concreteSession(self):
        if hasattr(self, 'tutorialSession'):
            return self.tutorialSession
        elif hasattr(self, 'blackenOutSession'):
            return self.blackenOutSession
        else:
            return None

    @property
    def userProfiles(self):
        return self.userProfileSet.all()


    def __str__(self):
        concreteSession = self.concreteSession
        return 'OccupiedSession <abstract>: ' + (concreteSession.__str__() if (concreteSession is not None) else 'Unknown!')



class TutorialSession(OccupiedSession):

    @classmethod
    def create(cls, studentRole, tutorRole, startDate, endDate, cancelled=False, locked=False):
        return cls.objects.create(
            userProfileSet = [studentRole, tutorRole],
            startDate = startDate,
            endDate = endDate,
            cancelled = cancelled,
            studentRole = studentRole,
            tutorRole = tutorRole,
            locked = locked
        )

    occupiedSession = models.OneToOneField(OccupiedSession, on_delete=models.CASCADE, parent_link=True, related_name='tutorialSession', related_query_name='tutorialSession')
    
    studentRole = models.ForeignKey('StudentRole', on_delete=models.PROTECT, related_name='tutorialSessions', related_query_name='tutorialSessions')
    tutorRole = models.ForeignKey('TutorRole', on_delete=models.PROTECT, related_name='tutorialSessions', related_query_name='tutorialSessions')
    locked = models.BooleanField(default=False)


    def __str__(self):
        return 'TutorialSession: {self.locked}'.format(self=self)



class BlackenOutSession(OccupiedSession):

    @classmethod
    def create(cls, tutorRole, startDate, endDate, cancelled=False):
        session = cls.objects.create(
            # userProfileSet = [tutorRole],
            startDate = startDate,
            endDate = endDate,
            cancelled = cancelled,
            tutorRole = tutorRole
        )
        session.userProfileSet = [tutorRole.userProfile]
        return session


    occupiedSession = models.OneToOneField(OccupiedSession, on_delete=models.CASCADE, parent_link=True, related_name='blackenOutSession', related_query_name='blackenOutSession')

    tutorRole = models.ForeignKey('TutorRole', on_delete=models.CASCADE, related_name='blackenOutSessionSet', related_query_name='blackenOutSessionSet')


    def __str__(self):
        return 'BlackenOutSession: {self.startDate} - {self.endDate} : {self.tutorRole}'.format(self=self)
