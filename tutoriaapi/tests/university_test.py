from django.test import TestCase

from ..models import *

university_data_0 = dict(
    name = 'HKU'
)

def assert_university_equal_data(test_case, university, **data):
    test_case.assertEqual(university.name, data['name'])


class UniversityTest(TestCase):

    def test_new_university(self):
        university = University.create(**university_data_0)
        assert_university_equal_data(self, university, **university_data_0)
