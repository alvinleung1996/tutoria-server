from django.db import models

from . import tutorial

class Student(models.Model):

    @classmethod
    def create(cls, user):
        return cls.objects.create(user=user)

    user = models.OneToOneField('User', on_delete=models.CASCADE, related_name='student', related_query_name='student')

    def add_tutorial(self, tutor, start_time, end_time):
        return tutorial.Tutorial.create(
            student = self,
            tutor = tutor,
            start_time = start_time,
            end_time = end_time,
        )
    

    def is_valid_tutorial_time(self, start_time, end_time):
        """Check if the input time is valid for this tutor

        Args:
            start_time: An aware datetime object.
            end_time: An aware datetime object.

        Returns:
            True if it is valid, False otherwise

        Raises:

        """
        return self.user.has_no_event(start_time, end_time)

    def __str__(self):
        return 'Student: {self.user.given_name} {self.user.family_name}'.format(self=self)
