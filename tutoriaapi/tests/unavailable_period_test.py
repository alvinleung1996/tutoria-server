from decimal import Decimal
from datetime import datetime, timezone, timedelta

from django.test import TestCase
from django.utils import timezone as djtimezone

from ..models import *

from . import user_test, student_test, tutor_test, university_test, course_code_test

def _get_time(hour, minute, year=None, month=None, day=None, day_offset=0):
    time = datetime.now(tz=djtimezone.get_default_timezone())
    time = time.replace(
        year = year if year is not None else time.year,
        month = month if month is not None else time.month,
        day = day if day is not None else time.day,
        hour = hour,
        minute = minute,
        second = 0,
        microsecond = 0
    )
    time += timedelta(days=day_offset)
    return time

unavailable_period_data_0 = dict(
    start_time = _get_time(13, 0, day_offset=1),
    end_time = _get_time(14, 00, day_offset=1)
)

unavailable_period_data_1 = dict(
    start_time = _get_time(13, 30, day_offset=1),
    end_time = _get_time(14, 00, day_offset=1)
)


def assert_unavailable_period_equal_data(test_case, unavailable_period, **data):
    test_case.assertEqual(unavailable_period.start_time, data['start_time'])
    test_case.assertEqual(unavailable_period.end_time, data['end_time'])


class UnavailablePeriodTest(TestCase):

    def test_create(self):
        university = University.create(**university_test.university_data_0)

        course_codes = [CourseCode.create(university=university, **course_code_test.course_code_data_0)]

        user_0 = User.create(**user_test.user_data_0)
        user_0.add_role(Tutor, **tutor_test.tutor_data_contracted_0, university=university, course_codes=course_codes)
        
        tutor = user_0.tutor

        unavailable_period = UnavailablePeriod.create(
            tutor = tutor,
            **unavailable_period_data_0
        )

        assert_unavailable_period_equal_data(self, unavailable_period, **unavailable_period_data_0)

        event = unavailable_period.event

        # UnavailablePeriod - Event
        self.assertIsNotNone(event)
        self.assertEqual(event.unavailable_period, unavailable_period)
        self.assertEqual(event.concrete_event, unavailable_period)

        # UnavailablePeriod - Tutor
        self.assertEqual(unavailable_period.tutor, tutor)
        self.assertListEqual(list(tutor.unavailable_period_set.all()), [unavailable_period])

        # Event - User
        self.assertListEqual(list(unavailable_period.user_set.all()), [user_0])

        self.assertListEqual(list(user_0.event_set.all()), [event])
        self.assertListEqual(list(user_0.event_set.filter(cancelled=False)), [event])
        self.assertTrue(user_0.has_no_event(
            start_time = unavailable_period_data_0['start_time'] - timedelta(microseconds=1),
            end_time = unavailable_period_data_0['start_time']
        ))
        self.assertFalse(user_0.has_no_event(
            start_time = unavailable_period_data_0['start_time'],
            end_time = unavailable_period_data_0['end_time']
        ))
        self.assertTrue(user_0.has_no_event(
            start_time = unavailable_period_data_0['end_time'],
            end_time = unavailable_period_data_0['end_time'] + timedelta(microseconds=1)
        ))

        unavailable_period.cancelled = True
        unavailable_period.save()

        self.assertListEqual(list(user_0.event_set.filter(cancelled=False)), [])
        self.assertTrue(user_0.has_no_event(
            start_time = unavailable_period_data_0['start_time'] - timedelta(microseconds=1),
            end_time = unavailable_period_data_0['start_time']
        ))
        self.assertTrue(user_0.has_no_event(
            start_time = unavailable_period_data_0['start_time'],
            end_time = unavailable_period_data_0['end_time']
        ))
        self.assertTrue(user_0.has_no_event(
            start_time = unavailable_period_data_0['end_time'],
            end_time = unavailable_period_data_0['end_time'] + timedelta(microseconds=1)
        ))

        # TODO: Add more assertion

