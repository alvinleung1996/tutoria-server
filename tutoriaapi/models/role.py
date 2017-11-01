from django.db import models
from .user import User

from .university import University
from .coursecode import CourseCode
from .event import UnavailablePeriod
from .review import Review

from decimal import Decimal


class Role(models.Model):

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='roleSet', related_query_name='roleSet')

    @property
    def concreteRole(self):
        if hasattr(self, 'student'):
            return self.student
        elif hasattr(self, 'tutor'):
            return self.tutor
        else:
            return None

    def __str__(self):
        concreteRole = self.concreteRole
        return 'Role <abstract>: ' + (concreteRole.__str__() if (concreteRole is not None) else 'Unknown!')



class Student(Role):

    @classmethod
    def create(cls, user):
        return cls.objects.create(user=user)

    role = models.OneToOneField(Role, on_delete=models.CASCADE, parent_link=True, related_name='student', related_query_name='student')

    def __str__(self):
        return 'Student: {self.user.givenName} {self.user.familyName}'.format(self=self)



class SubjectTag(models.Model):

    @classmethod
    def create(cls, tutor, tag):
        return cls.objects.create(tutor=tutor, tag=tag)

    tutor = models.ForeignKey('Tutor', on_delete=models.CASCADE, related_name='subjectTagSet', related_query_name='subjectTagSet')

    tag = models.CharField(max_length=10)

    def __str__(self):
        return 'SubjectTag: "{self.tag}"'.format(self=self)



class Tutor(Role):

    TYPE_PRIVATE = 'PR'
    TYPE_CONTRACTED = 'CO'

    @classmethod
    def create(cls, user, type, activated, university, courseCodes, subjectTags=[]):
        return cls.objects.create(
            user = user,
            type = type,
            activated = activated,
            university = university,
            courseCodeSet = courseCodes,
            subjectTagSet = subjectTags
        )
        

    role = models.OneToOneField(Role, on_delete=models.CASCADE, parent_link=True, related_name='tutor', related_query_name='tutor')

    type = models.CharField(max_length=2, choices=(
        (TYPE_PRIVATE, 'Private'),
        (TYPE_CONTRACTED, 'Contracted')
    ), default=TYPE_PRIVATE)

    biography = models.TextField()

    hourlyRate = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal(0))

    activated = models.BooleanField(default=True)

    university = models.ForeignKey(University, on_delete=models.PROTECT, related_name='tutorSet', related_query_name='tutorSet')

    courseCodeSet = models.ManyToManyField(CourseCode, related_name='tutorSet', related_query_name='tutorSet')

    @property
    def averageReviewScore(self):
        sum = 0
        length = 0
        for entry in Review.objects.filter(tutorial__tutor=self):
            sum += entry.score
            length += 1
        return sum / length if length != 0 else -1


    def addUnavailablePeriod(self, startDate, endDate):
        return UnavailablePeriod.create(
            tutor = self,
            startDate = startDate,
            endDate = endDate,
            cancelled = False
        )


    def __str__(self):
        return 'Tutor: {self.user.givenName} {self.user.familyName}'.format(self=self)
