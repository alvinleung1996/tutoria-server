from django.db import models
from .user import User

from .university import University
from .course_code import CourseCode
from .event import UnavailablePeriod
from .review import Review

from decimal import Decimal


class Role(models.Model):

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='role_set', related_query_name='role_set')

    @property
    def concrete_role(self):
        if hasattr(self, 'student'):
            return self.student
        elif hasattr(self, 'tutor'):
            return self.tutor
        else:
            return None

    def __str__(self):
        concrete_role = self.concrete_role
        return 'Role <abstract>: ' + (concrete_role.__str__() if (concrete_role is not None) else 'Unknown!')



class Student(Role):

    @classmethod
    def create(cls, user):
        return cls.objects.create(user=user)

    role = models.OneToOneField(Role, on_delete=models.CASCADE, parent_link=True, related_name='student', related_query_name='student')

    def __str__(self):
        return 'Student: {self.user.given_name} {self.user.family_name}'.format(self=self)



class SubjectTag(models.Model):

    @classmethod
    def create(cls, tutor, tag):
        return cls.objects.create(tutor=tutor, tag=tag)

    tutor = models.ForeignKey('Tutor', on_delete=models.CASCADE, related_name='subject_tag_set', related_query_name='subject_tag_set')

    tag = models.CharField(max_length=10)

    def __str__(self):
        return 'SubjectTag: "{self.tag}"'.format(self=self)



class Tutor(Role):

    TYPE_PRIVATE = 'PR'
    TYPE_CONTRACTED = 'CO'

    @classmethod
    def create(cls, user, type, activated, university, course_codes, subject_tags=[]):
        return cls.objects.create(
            user = user,
            type = type,
            activated = activated,
            university = university,
            course_code_set = course_codes,
            subject_tag_set = subject_tags
        )
        

    role = models.OneToOneField(Role, on_delete=models.CASCADE, parent_link=True, related_name='tutor', related_query_name='tutor')

    type = models.CharField(max_length=2, choices=(
        (TYPE_PRIVATE, 'Private'),
        (TYPE_CONTRACTED, 'Contracted')
    ), default=TYPE_PRIVATE)

    biography = models.TextField()

    hourly_rate = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal(0))

    activated = models.BooleanField(default=True)

    university = models.ForeignKey(University, on_delete=models.PROTECT, related_name='tutor_set', related_query_name='tutor_set')

    course_code_set = models.ManyToManyField(CourseCode, related_name='tutor_set', related_query_name='tutor_set')

    @property
    def average_review_score(self):
        sum = 0
        length = 0
        for entry in Review.objects.filter(tutorial__tutor=self):
            sum += entry.score
            length += 1
        return sum / length if length != 0 else -1


    def add_unavailable_period(self, start_date, end_date):
        return UnavailablePeriod.create(
            tutor = self,
            start_date = start_date,
            end_date = end_date,
            cancelled = False
        )


    def __str__(self):
        return 'Tutor: {self.user.given_name} {self.user.family_name}'.format(self=self)
