from django.test import TestCase

from ..models import *

from . import message_test

user_data_0 = dict(
    username = 'alvin',
    password = 'alvinalvin',
    email = 'a@a.com',
    given_name = 'Alvin',
    family_name = 'Leung',
    phone_number = '12345678',
    avatar = ''
)

user_data_1 = dict(
    username = 'peter',
    password = 'peterpeter',
    email = 'p@p.com',
    given_name = 'Peter',
    family_name = 'Lee',
    phone_number = '12345678',
    avatar = ''
)

user_data_2 = dict(
    username = 'george',
    password = 'georgegeorge',
    email = 'g@g.com',
    given_name = 'George',
    family_name = 'Trump',
    phone_number = '12345678',
    avatar = ''
)

def assert_user_equal_data(test_case, user, **data):
    test_case.assertEqual(user.username, data['username'])
    test_case.assertNotEqual(user.password, data['password'])
    test_case.assertEqual(user.email, data['email'])
    test_case.assertEqual(user.given_name, data['given_name'])
    test_case.assertEqual(user.family_name, data['family_name'])
    test_case.assertEqual(user.phone_number, data['phone_number'])
    test_case.assertEqual(user.avatar, data['avatar'])


class UserTest(TestCase):

    def test_new_user(self):
        user = User.create(**user_data_0)
        assert_user_equal_data(self, user, **user_data_0)
        self.assertIsNone(user.get_role(Student))
        self.assertIsNone(user.get_role(Tutor))
        self.assertIsNone(user.get_role(Company))
        self.assertIsNotNone(user.wallet)
    
    def test_send_message(self):
        send_user = User.create(**user_data_0)
        receive_user = User.create(**user_data_1)
        message = send_user.send_message(receive_user, **message_test.message_data_0)
        self.assertIn(message, send_user.send_message_set.all())
        self.assertIn(message, receive_user.receive_message_set.all())
