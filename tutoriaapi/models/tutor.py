from decimal import Decimal
from datetime import datetime, timezone, timedelta

from django.db import models
from django.utils import timezone as djtimezone

from . import university, course_code, unavailable_period, review


class SubjectTag(models.Model):

    @classmethod
    def create(cls, tutor, tag):
        return cls.objects.create(tutor=tutor, tag=tag)

    tutor = models.ForeignKey('Tutor', on_delete=models.CASCADE, related_name='subject_tag_set', related_query_name='subject_tag_set')

    tag = models.CharField(max_length=10)

    def __str__(self):
        return 'SubjectTag: "{self.tag}"'.format(self=self)



class Tutor(models.Model):

    TYPE_PRIVATE = 'PR'
    TYPE_CONTRACTED = 'CO'

    @classmethod
    def create(cls, user, type, biography, university, course_codes, subject_tags=None, hourly_rate=Decimal('0'), activated=True):
        if subject_tags is None:
            subject_tags = []
        
        tutor = cls.objects.create(
            user = user,
            type = type,
            biography = biography,
            hourly_rate = hourly_rate,
            activated = activated,
            university = university
        )
        tutor.course_code_set.set(course_codes)
        for tag in subject_tags:
            tutor.subject_tag_set.add(tag if isinstance(tag, SubjectTag) else SubjectTag.create(tutor, tag))
        return tutor


    user = models.OneToOneField('User', on_delete=models.CASCADE, related_name='tutor', related_query_name='tutor')

    type = models.CharField(max_length=2, choices=(
        (TYPE_PRIVATE, 'Private'),
        (TYPE_CONTRACTED, 'Contracted')
    ), default=TYPE_PRIVATE)

    biography = models.TextField()

    hourly_rate = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0'))

    activated = models.BooleanField(default=True)

    university = models.ForeignKey('University', on_delete=models.PROTECT, related_name='tutor_set', related_query_name='tutor_set')

    course_code_set = models.ManyToManyField('CourseCode', related_name='tutor_set', related_query_name='tutor_set')

    @property
    def average_review_score(self):
        sum = 0
        length = 0
        for entry in review.Review.objects.filter(tutorial__tutor=self):
            sum += entry.score
            length += 1
        return sum / length if length != 0 else -1


    def is_valid_tutorial_time(self, start_time, end_time):
        """Check if the input time is valid for this tutor

        Args:
            start_time: An aware datetime object.
            end_time: An aware datetime object.

        Returns:
            True if it is valid, False otherwise

        Raises:

        """
        # Convert to local time
        start_time = start_time.astimezone(djtimezone.get_default_timezone())
        end_time = end_time.astimezone(djtimezone.get_default_timezone())

        if end_time < start_time:
            raise ValueError('end_time before start_time')

        current_time = datetime.now(tz=djtimezone.get_default_timezone())

        # if current_time > start_time
        if start_time < current_time:
            raise ValueError('start_time has passed')

        # if start_time < 24 hours to start
        if (start_time - current_time) < timedelta(days=1):
            return False

        # if the start_time is not HH:00 or HH:30 (depending on the tutor type)
        if (start_time.second != 0 or start_time.microsecond != 0
                or (self.type == self.TYPE_CONTRACTED and start_time.minute not in [0])
                or (self.type == self.TYPE_PRIVATE and start_time.minute not in [0, 30])):
            return False

        if (end_time - start_time) not in ([timedelta(minutes=30)] if (self.type == self.TYPE_CONTRACTED) else [timedelta(minutes=30), timedelta(minutes=60)]):
            return False

        local_day_start_time = start_time.astimezone(djtimezone.get_current_timezone()).replace(
            hour = 0, minute = 0, second = 0, microsecond = 0
        )
        local_day_end_time = local_day_start_time + timedelta(days=1)

        # if student has already book one tutorial on the sam day
        if not self.user.has_no_event(local_day_start_time, local_day_end_time):
            return False

        return True

    def calc_tutorial_fee(self, start_time, end_time):
        """Calculate the tutorial fee

        Args:
            start_time: An aware datetime object.
            end_time: An aware datetime object.

        Returns:
            Decimal object representing the fee

        Raises:
            ValueError: end_time is before start_time
        """
        # Convert to local time
        start_time = start_time.astimezone(djtimezone.get_default_timezone())
        end_time = end_time.astimezone(djtimezone.get_default_timezone())

        if end_time < start_time:
            raise ValueError('end_time before start_time')

        if self.type == self.TYPE_CONTRACTED:
            return Decimal('0')
        
        duration = end_time - start_time
        fee = self.hourly_rate * (Decimal(duration.total_seconds()) / Decimal(timedelta(hours=1).total_seconds()))
        
        return fee


    def add_unavailable_period(self, start_time, end_time):
        return unavailable_period.UnavailablePeriod.create(
            tutor = self,
            start_time = start_time,
            end_time = end_time,
            cancelled = False
        )


    def __str__(self):
        return 'Tutor: {self.user.given_name} {self.user.family_name}'.format(self=self)
