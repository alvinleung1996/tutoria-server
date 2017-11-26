from decimal import Decimal
from datetime import datetime, timezone

from django.test import TestCase

from ..models import *

from . import user_test, wallet_test


def assert_transaction_equal_data(test_case, transaction, **data):
    test_case.assertEqual(transaction.amount, data['amount'])
    test_case.assertEqual(transaction.time, data['time'])

class TransactionTest(TestCase):

    def test_new_transaction(self):
        user_0 = User.create(**user_test.user_data_0, balance=Decimal('500'))
        user_1 = User.create(**user_test.user_data_1)

        wallet_0 = user_0.wallet
        wallet_1 = user_1.wallet

        amount = Decimal('50')
        wallet_0_target_balance = wallet_0.balance - amount
        wallet_1_target_balance = wallet_1.balance + amount

        time = datetime.now(tz=timezone.utc)
        transaction = Transaction.create(withdraw=wallet_0, deposit=wallet_1, amount=amount, time=time)

        assert_transaction_equal_data(self, transaction, amount=amount, time=time)
        self.assertEqual(wallet_0.balance, wallet_0_target_balance)
        self.assertEqual(wallet_1.balance, wallet_1_target_balance)


    def test_new_transaction_insufficient(self):
        user_0 = User.create(**user_test.user_data_0, balance=Decimal('10'))
        user_1 = User.create(**user_test.user_data_1)

        wallet_0 = user_0.wallet
        wallet_1 = user_1.wallet

        amount = Decimal('50')
        wallet_0_ori_balance = wallet_0.balance
        wallet_1_ori_balance = wallet_1.balance

        with self.assertRaises(Wallet.InsufficientBalanceError):
            Transaction.create(withdraw=wallet_0, deposit=wallet_1, amount=amount)
        
        self.assertEqual(wallet_0.balance, wallet_0_ori_balance)
        self.assertEqual(wallet_1.balance, wallet_1_ori_balance)

