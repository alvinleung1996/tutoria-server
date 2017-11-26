from django.test import TestCase

from ..models import *

from . import user_test

company_data_0 = dict()

def assert_company_equal_data(test_case, company, **data):
    pass

class CompanyTest(TestCase):

    def test_new_company(self):
        user = User.create(**user_test.user_data_0)
        company = Company.create(user, **company_data_0)
        assert_company_equal_data(self, company, **company_data_0)
        self.assertEqual(company.user, user)
        self.assertEqual(user.company, company)
        self.assertEqual(user.get_role(Company), company)

    def test_add_company(self):
        user = User.create(**user_test.user_data_0)
        user.add_role(Company, **company_data_0)
        company = user.get_role(Company)
        assert_company_equal_data(self, company, **company_data_0)
        self.assertEqual(company.user, user)
        self.assertEqual(user.company, company)
    