from decimal import Decimal
from datetime import datetime, timezone, timedelta

from django.test import TestCase
from django.utils import timezone as djtimezone

from ..models import *

from . import user_test, student_test, tutor_test, university_test, course_code_test, company_test

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

tutorial_data_contracted_0 = dict(
    start_time = _get_time(13, 0, day_offset=1),
    end_time = _get_time(13, 30, day_offset=1)
)

tutorial_data_private_0 = dict(
    start_time = _get_time(13, 0, day_offset=1),
    end_time = _get_time(13, 30, day_offset=1)
)


def assert_tutorial_equal_data(test_case, tutorial, **data):
    test_case.assertEqual(tutorial.start_time, data['start_time'])
    test_case.assertEqual(tutorial.end_time, data['end_time'])

class TutorialTest(TestCase):

    def test_create_contracted(self):
        university = University.create(**university_test.university_data_0)

        course_codes = [CourseCode.create(university=university, **course_code_test.course_code_data_0)]

        user_0 = User.create(**user_test.user_data_0)
        user_0.add_role(Student, **student_test.student_data_0)

        user_1 = User.create(**user_test.user_data_1)
        user_1.add_role(Tutor, **tutor_test.tutor_data_contracted_0, university=university, course_codes=course_codes)

        user_2 = User.create(**user_test.user_data_2)
        user_2.add_role(Company, **company_test.company_data_0)
        
        student = user_0.student
        tutor = user_1.tutor

        tutorial = Tutorial.create(
            student = student,
            tutor = tutor,
            **tutorial_data_contracted_0
        )

        assert_tutorial_equal_data(self, tutorial, **tutorial_data_contracted_0)

        event = tutorial.event

        self.assertIsNotNone(event)
        self.assertIsNotNone(event.tutorial)
        self.assertEqual(event.concrete_event, tutorial)

        self.assertListEqual(list(event.user_set.all()), [user_0, user_1])
        self.assertIn(event, user_0.event_set.all())
        self.assertIn(event, user_1.event_set.all())

        self.assertEqual(tutorial.student, student)
        self.assertEqual(tutorial.tutor, tutor)
        self.assertIn(tutorial, student.tutorial_set.all())
        self.assertIn(tutorial, tutor.tutorial_set.all())

        [u.wallet.refresh_from_db() for u in [user_0, user_1, user_2]]
        self.assertEqual(user_0.wallet.balance, Decimal('0'))
        self.assertEqual(user_1.wallet.balance, Decimal('0'))
        self.assertEqual(user_2.wallet.balance, Decimal('0'))

        self.assertIsNone(tutorial.student_to_company_transaction)
        self.assertIsNone(tutorial.company_to_tutor_transaction)
        self.assertIsNone(tutorial.company_to_student_transaction)

        tutorial.pay_to_tutor()

        [u.wallet.refresh_from_db() for u in [user_0, user_1, user_2]]
        self.assertEqual(user_0.wallet.balance, Decimal('0'))
        self.assertEqual(user_1.wallet.balance, Decimal('0'))
        self.assertEqual(user_2.wallet.balance, Decimal('0'))

        self.assertIsNone(tutorial.student_to_company_transaction)
        self.assertIsNone(tutorial.company_to_tutor_transaction)
        self.assertIsNone(tutorial.company_to_student_transaction)

        tutorial.refund()

        self.assertEqual(user_0.wallet.balance, Decimal('0'))
        self.assertEqual(user_1.wallet.balance, Decimal('0'))
        self.assertEqual(user_2.wallet.balance, Decimal('0'))

        self.assertIsNone(tutorial.student_to_company_transaction)
        self.assertIsNone(tutorial.company_to_tutor_transaction)
        self.assertIsNone(tutorial.company_to_student_transaction)

        # TODO: Add more assertion


    def test_create_private(self):
        university = University.create(**university_test.university_data_0)

        course_codes = [CourseCode.create(university=university, **course_code_test.course_code_data_0)]

        user_0 = User.create(**user_test.user_data_0, balance=Decimal('100'))
        user_0.add_role(Student, **student_test.student_data_0)

        user_1 = User.create(**user_test.user_data_1)
        # hourly rate is $30
        user_1.add_role(Tutor, **tutor_test.tutor_data_private_0, university=university, course_codes=course_codes)

        user_2 = User.create(**user_test.user_data_2)
        user_2.add_role(Company, **company_test.company_data_0)
        
        student = user_0.student
        tutor = user_1.tutor

        # book for half an hour
        tutorial = Tutorial.create(
            student = student,
            tutor = tutor,
            **tutorial_data_private_0
        )

        assert_tutorial_equal_data(self, tutorial, **tutorial_data_private_0)

        [u.wallet.refresh_from_db() for u in [user_0, user_1, user_2]]
        self.assertEqual(user_0.wallet.balance, Decimal('84.25'))
        self.assertEqual(user_1.wallet.balance, Decimal('0'))
        self.assertEqual(user_2.wallet.balance, Decimal('15.75'))

        self.assertIsNotNone(tutorial.student_to_company_transaction)
        self.assertIsNone(tutorial.company_to_tutor_transaction)
        self.assertIsNone(tutorial.company_to_student_transaction)

        tutorial.pay_to_tutor()

        [u.wallet.refresh_from_db() for u in [user_0, user_1, user_2]]
        self.assertEqual(user_0.wallet.balance, Decimal('84.25'))
        self.assertEqual(user_1.wallet.balance, Decimal('15'))
        self.assertEqual(user_2.wallet.balance, Decimal('0.75'))

        self.assertIsNotNone(tutorial.student_to_company_transaction)
        self.assertIsNotNone(tutorial.company_to_tutor_transaction)
        self.assertIsNone(tutorial.company_to_student_transaction)

        # TODO: Add more assertion
        
