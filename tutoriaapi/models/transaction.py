from decimal import Decimal
from datetime import datetime, timezone

from django.db import models, transaction

from . import wallet

class Transaction(models.Model):

    @classmethod
    def create(cls, withdraw, deposit, amount, time=None):
        if time is None:
            time = datetime.now(tz=timezone.utc)

        withdraw_wallet = withdraw if isinstance(withdraw, wallet.Wallet) else withdraw.wallet
        deposit_wallet = deposit if isinstance(deposit, wallet.Wallet) else deposit.wallet

        with transaction.atomic():
            withdraw_wallet.withdraw(amount)
            deposit_wallet.deposit(amount)

        return cls.objects.create(
            amount = amount,
            withdraw_wallet = withdraw_wallet,
            deposit_wallet = deposit_wallet,
            time = time
        )

    amount = models.DecimalField(max_digits=10, decimal_places=2)

    withdraw_wallet = models.ForeignKey('Wallet', on_delete=models.SET_NULL, related_name='withdraw_transaction_set', related_query_name='withdraw_transaction', null=True)

    deposit_wallet = models.ForeignKey('Wallet', on_delete=models.SET_NULL, related_name='deposit_transaction_set', related_query_name='deposit_transaction', null=True)

    time = models.DateTimeField(null=True, default=None)


    # A method to retrieve who is the transaction creator
    # A tutorial? or something else
    #
    # @property
    # def reason(self):
    #     if hasattr(self, 'tutorial'):
    #         return self.tutorial
    #     else:
    #         return None
        