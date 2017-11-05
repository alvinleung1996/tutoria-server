from django.test import TestCase

from ..models import *

from . import user_test

message_data_0 = dict(
    title = 'Mt Title',
    content = 'Hello World!!!'
)

def assert_message_equal_data(test_case, message, **data):
    test_case.assertEqual(message.title, data['title'])
    test_case.assertEqual(message.content, data['content'])

class MessageTest(TestCase):

    def test_new_message(self):
        user_0 = User.create(**user_test.user_data_0)
        user_1 = User.create(**user_test.user_data_1)
        message = Message.create(user_0, user_1, **message_data_0)
        assert_message_equal_data(self, message, **message_data_0)
        self.assertEqual(message.send_user, user_0)
        self.assertEqual(message.receive_user, user_1)
        self.assertListEqual(list(user_0.send_message_set.all()), [message])
        self.assertListEqual(list(user_1.receive_message_set.all()), [message])