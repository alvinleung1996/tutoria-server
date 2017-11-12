from django.test import TestCase

from ..models import *

from . import time_utils

coupon_data_0 = dict(
    code = 'abcd1234',
    start_time = time_utils.get_time(hour=0, minute=0, day_offset=-1),
    end_time = time_utils.get_time(hour=0, minute=0, day_offset=1)
)

def assert_coupon_equal_data(test_case, coupon, **data):
    test_case.assertEqual(coupon.code, data['code'])
    test_case.assertEqual(coupon.start_time, data['start_time'])
    test_case.assertEqual(coupon.end_time, data['end_time'])

class CouponTest(TestCase):

    def test_new_coupon(self):
        coupon = Coupon.create(**coupon_data_0)
        assert_coupon_equal_data(self, coupon, **coupon_data_0)
        self.assertTrue(coupon.is_valid_now())
