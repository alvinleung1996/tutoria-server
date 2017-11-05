from datetime import datetime, timedelta

from django.utils import timezone as djtimezone
from django.test import TestCase

from ..models import *

from . import user_test

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

event_data_0 = dict(
    start_time = _get_time(13, 0),
    end_time = _get_time(14, 0)
)

def assert_event_equal_data(test_case, event, **data):
    test_case.assertEqual(event.start_time, data['start_time'])
    test_case.assertEqual(event.end_time, data['end_time'])

class EventTest(TestCase):

    def test_create(self):
        user_0 = User.create(**user_test.user_data_0)

        event = Event.create(users=[user_0], **event_data_0)

        assert_event_equal_data(self, event, **event_data_0)
        
        self.assertEqual(event.user_set.count(), 1)
        self.assertEqual(user_0.event_set.count(), 1)
        self.assertIn(user_0, event.user_set.all())
        self.assertIn(event, user_0.event_set.all())

        self.assertEqual(user_0.event_set.filter(cancelled=False).count(), 1)
        self.assertIn(event, user_0.event_set.filter(cancelled=False).all())

        event.cancelled = True
        event.save()

        self.assertEqual(user_0.event_set.filter(cancelled=False).count(), 0)
        self.assertNotIn(event, user_0.event_set.filter(cancelled=False).all())
