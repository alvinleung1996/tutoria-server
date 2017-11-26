from decimal import Decimal

from django.test import TestCase

from ..models import *

from . import user_test

wallet_data_0 = dict(
    balance = Decimal('100')
)

def assert_wallet_equal_data(test_case, wallet, **data):
    test_case.assertEqual(wallet.balance, data['balance'])

class WalletTest(TestCase):

    def test_new_wallet(self):
        user = User.create(**user_test.user_data_0, **wallet_data_0)
        wallet = user.wallet
        assert_wallet_equal_data(self, wallet, **wallet_data_0)
        self.assertEqual(wallet.user, user)
    
    def test_withdraw(self):
        user = User.create(**user_test.user_data_0, **wallet_data_0)
        wallet = user.wallet
        ori_balance = wallet.balance
        amount = Decimal('50')
        target_balance = ori_balance - amount
        wallet.withdraw(amount)
        self.assertEqual(wallet.balance, target_balance)
    
    def test_withdraw_insufficient_amount(self):
        user = User.create(**user_test.user_data_0, **wallet_data_0)
        wallet = user.wallet
        ori_balance = wallet.balance
        amount = ori_balance + Decimal('100')
        with self.assertRaises(Wallet.InsufficientBalanceError):
            wallet.withdraw(amount)
        self.assertEqual(wallet.balance, ori_balance)
    
    def test_deposit(self):
        user = User.create(**user_test.user_data_0, **wallet_data_0)
        wallet = user.wallet
        ori_balance = wallet.balance
        amount = Decimal('50')
        target_balance = ori_balance + amount
        wallet.deposit(amount)
        self.assertEqual(wallet.balance, target_balance)
