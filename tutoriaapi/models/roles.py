from django.db import models
from .userprofile import UserProfile

from .university import University
from .coursecode import CourseCode
from .occupiedsessions import BlackenOutSession


class Role(models.Model):

    userProfile = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='roleSet', related_query_name='roleSet')

    @property
    def concreteRole(self):
        if hasattr(self, 'studentRole'):
            return self.studentRole
        elif hasattr(self, 'tutorRole'):
            return self.tutorRole
        else:
            return None

    def __str__(self):
        concreteRole = self.concreteRole
        return 'Role <abstract>: ' + (concreteRole.__str__() if (concreteRole is not None) else 'Unknown!')



class StudentRole(Role):

    @classmethod
    def create(cls, userProfile):
        return cls.objects.create(userProfile=userProfile)

    role = models.OneToOneField(Role, on_delete=models.CASCADE, parent_link=True, related_name='studentRole', related_query_name='studentRole')

    @property
    def tutorialSessions(self):
        return self.tutorialSessionSet.all()

    def __str__(self):
        return 'StudentRole: {self.userProfile.givenName} {self.userProfile.familyName}'.format(self=self)



class TutorRoleSubjectTag(models.Model):

    @classmethod
    def create(cls, tutorRole, tag):
        return cls.objects.create(tutorRole=tutorRole, tag=tag)

    tutorRole = models.ForeignKey('TutorRole', on_delete=models.CASCADE, related_name='subjectTagSet', related_query_name='subjectTagSet')

    tag = models.CharField(max_length=10)

    def __str__(self):
        return 'SubjectTag: "{self.tag}"'.format(self=self)



class TutorRole(Role):

    TYPE_PRIVATE = 'PR'
    TYPE_CONTRACTED = 'CO'

    @classmethod
    def create(cls, userProfile, type, activated, university, courseCode, subjectTags=[]):
        tutorRole = cls.objects.create(
            userProfile = userProfile,
            type = type,
            activated = activated,
            university = university,
            courseCode = courseCode
        )
        for tag in subjectTags:
            TutorRoleSubjectTag.create(tutorRole, tag)
        return tutorRole
        

    role = models.OneToOneField(Role, on_delete=models.CASCADE, parent_link=True, related_name='tutorRole', related_query_name='tutorRole')

    type = models.CharField(max_length=2, choices=(
        (TYPE_PRIVATE, 'Private'),
        (TYPE_CONTRACTED, 'Contracted')
    ), default=TYPE_PRIVATE)

    activated = models.BooleanField(default=True)

    university = models.ForeignKey(University, on_delete=models.PROTECT, related_name='tutorRoleSet', related_query_name='tutorRoleSet')

    courseCode = models.ForeignKey(CourseCode, on_delete=models.PROTECT, related_name='tutorRoleSet', related_query_name='tutorRoleSet')


    @property
    def subjectTags(self):
        return self.subjectTagSet.all()

    @property
    def tutorialSessions(self):
        return self.tutorialSessionSet.all()

    @property
    def blackenOutSessions(self):
        return self.blackenOutSessionSet.all()

    @property
    def averageRatingScore(self):
        sum = 0
        length = 0
        for i in map(lambda s: s.review.ratingScore, filter(lambda s: s.review is not None, self.tutorialSessions)):
            sum += i
            length = length + 1
        return sum / length


    def addBlackenOutSession(self, startDate, endDate):
        return BlackenOutSession.create(
            tutorRole = self,
            startDate = startDate,
            endDate = endDate,
            cancelled = False
        )


    def __str__(self):
        return 'TutorRole: {self.userProfile.givenName} {self.userProfile.familyName}'.format(self=self)
