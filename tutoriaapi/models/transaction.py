from decimal import Decimal
from datetime import datetime, timezone

from django.db import models, transaction

from . import wallet, user

from ..api_exception import ApiException

class Transaction(models.Model):

    @classmethod
    def create(cls, withdraw, deposit, amount, time=None):
        if time is None:
            time = datetime.now(tz=timezone.utc)

        if isinstance(withdraw, user.User):
            withdraw_wallet = withdraw.wallet
        else:
            withdraw_wallet = withdraw
        
        if isinstance(deposit, user.User):
            deposit_wallet = deposit.wallet
        else:
            deposit_wallet = deposit
        
        if withdraw_wallet is None and deposit_wallet is None:
            raise ApiException(message='Cannot create transaction with both deposit and withdraw is None')

        with transaction.atomic():
            if withdraw_wallet is not None:
                withdraw_wallet.withdraw(amount)
            if deposit_wallet is not None:
                deposit_wallet.deposit(amount)

        return cls.objects.create(
            amount = amount,
            withdraw_wallet = withdraw_wallet,
            deposit_wallet = deposit_wallet,
            time = time
        )

    amount = models.DecimalField(max_digits=10, decimal_places=2)

    withdraw_wallet = models.ForeignKey('Wallet', on_delete=models.SET_NULL, related_name='withdraw_transaction_set', related_query_name='withdraw_transaction', null=True, blank=True)

    deposit_wallet = models.ForeignKey('Wallet', on_delete=models.SET_NULL, related_name='deposit_transaction_set', related_query_name='deposit_transaction', null=True, blank=True)

    time = models.DateTimeField(null=True, default=None)

    
    def __str__(self):
        string = 'Transaction:'
        if self.withdraw_wallet is not None:
            string += ' From "' + self.withdraw_wallet.user.full_name + '"'
        if self.deposit_wallet is not None:
            string += ' To "' + self.deposit_wallet.user.full_name + '"'
        string += " Amount: " + str(self.amount)
        return string
        