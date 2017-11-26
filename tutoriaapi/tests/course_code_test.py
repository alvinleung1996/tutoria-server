from django.test import TestCase

from ..models import *

from . import university_test

course_code_data_0 = dict(
    code = 'COMP3297'
)

def assert_course_code_equal_data(test_case, course_code, **data):
    test_case.assertEqual(course_code.code, data['code'])


class CourseCodeTest(TestCase):

    def test_new_course_code(self):
        university = University.create(**university_test.university_data_0)
        course_code = CourseCode.create(university=university, **course_code_data_0)
        assert_course_code_equal_data(self, course_code, **course_code_data_0)
        self.assertEqual(course_code.university, university)
        self.assertIn(course_code, university.course_code_set.all())
