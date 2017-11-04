from decimal import Decimal

from django.test import TestCase

from ..models import *

from . import user_test, university_test, course_code_test

tutor_data_0 = dict(
    type = Tutor.TYPE_CONTRACTED,
    biography = 'This is my biography',
    hourly_rate = Decimal('0'),
    activated = True,
    subject_tags = ['Tag0', 'Tag1']
)

tutor_data_1 = dict(
    type = Tutor.TYPE_CONTRACTED,
    biography = 'I am a private tutor',
    hourly_rate = Decimal('30'),
    activated = True,
    subject_tags = ['Tag2', 'Tag3']
)

def assert_tutor_equal_data(test_case, tutor, **data):
    test_case.assertEqual(tutor.type, data['type'])
    test_case.assertEqual(tutor.biography, data['biography'])
    test_case.assertEqual(tutor.hourly_rate, data['hourly_rate'])
    test_case.assertEqual(tutor.activated, data['activated'])
    test_case.assertListEqual([t.tag for t in tutor.subject_tag_set.all()], data['subject_tags'])

class TutorTest(TestCase):

    def test_new_tutor(self):
        user = User.create(**user_test.user_data_0)
        university = University.create(**university_test.university_data_0)
        course_codes = [
            CourseCode.create(university=university, **course_code_test.course_code_data_0)
        ]

        tutor = Tutor.create(
            user = user,
            university = university,
            course_codes = course_codes,
            **tutor_data_0
        )

        assert_tutor_equal_data(self, tutor, **tutor_data_0)
        self.assertEqual(tutor.user, user)
        self.assertEqual(user.tutor, tutor)
        self.assertEqual(user.get_role(Tutor), tutor)
        self.assertEqual(tutor.university, university)
        self.assertIn(tutor, university.tutor_set.all())
        self.assertListEqual(list(tutor.course_code_set.all()), course_codes)
        for course_code in course_codes:
            self.assertIn(tutor, course_code.tutor_set.all())


    def test_add_tutor(self):
        user = User.create(**user_test.user_data_0)
        university = University.create(**university_test.university_data_0)
        course_codes = [
            CourseCode.create(university=university, **course_code_test.course_code_data_0)
        ]

        tutor = user.add_role(Tutor,
            university = university,
            course_codes = course_codes,
            **tutor_data_0
        )

        assert_tutor_equal_data(self, tutor, **tutor_data_0)
        self.assertEqual(tutor.user, user)
        self.assertEqual(user.tutor, tutor)
        self.assertEqual(tutor.university, university)
        self.assertIn(tutor, university.tutor_set.all())
        self.assertListEqual(list(tutor.course_code_set.all()), course_codes)
        for course_code in course_codes:
            self.assertIn(tutor, course_code.tutor_set.all())
        