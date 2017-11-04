from django.test import TestCase

from ..models import *

from . import user_test

student_data_0 = dict()

def assert_student_equal_data(test_case, student, **data):
    pass

class StudentTest(TestCase):

    def test_new_student(self):
        user = User.create(**user_test.user_data_0)
        student = Student.create(user, **student_data_0)
        assert_student_equal_data(self, student, **student_data_0)
        self.assertEqual(student.user, user)
        self.assertEqual(user.student, student)
        self.assertEqual(user.get_role(Student), student)

    def test_add_student(self):
        user = User.create(**user_test.user_data_0)
        user.add_role(Student, **student_data_0)
        student = user.get_role(Student)
        assert_student_equal_data(self, student, **student_data_0)
        self.assertEqual(student.user, user)
        self.assertEqual(user.student, student)
    