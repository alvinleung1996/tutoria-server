from decimal import Decimal

from django.db import models, transaction

from . import message, user

from ..api_exception import ApiException

class Wallet(models.Model):

    class InsufficientBalanceError(ApiException):
        def __init__(self):
            super().__init__(message='There are no enough balance in the wallet')

    @classmethod
    def create(cls, user, balance=Decimal('0'), **kwargs):
        return cls.objects.create(
            user = user,
            balance = balance
        )
    
    
    # https://medium.com/@hakibenita/how-to-manage-concurrency-in-django-models-b240fed4ee2
    # https://docs.djangoproject.com/en/1.11/topics/db/transactions/
    # https://docs.djangoproject.com/en/1.11/ref/models/querysets/#select-for-update


    user = models.OneToOneField('User', on_delete=models.CASCADE, related_name='wallet', related_query_name='wallet')

    balance = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0'))

    def withdraw(self, amount, reason=None):
        with transaction.atomic():
            wallet_row = type(self).objects.select_for_update().get(pk=self.pk)
            if wallet_row.balance >= amount:
                wallet_row.balance -= amount
                wallet_row.save()
                self.refresh_from_db()
            else:
                raise self.InsufficientBalanceError()

        #notification when money move out of wallet
        title = '${0:.2f} is withdrawed from your wallet'.format(amount)
        content = '${0:.2f} is withdrawed from your wallet.'.format(amount)
        if isinstance(reason, str):
            content = content + reason
        content = (content +  ' If you find that this should not be happened,'
                    + ' please contact our systme administrator immediately.')
        message.Message.create(
            send_user = None,
            receive_user = self.user,
            title = title,
            content = content
        )
    
    def deposit(self, amount, reason=None):
        with transaction.atomic():
            wallet_row = type(self).objects.select_for_update().get(pk=self.pk)
            wallet_row.balance += amount
            wallet_row.save()
            self.refresh_from_db()
        
        #notification when money move into the wallet
        title = '${0:.2f} is deposited into your wallet'.format(amount)
        content = '${0:.2f} is deposited from your wallet.'.format(amount)
        if isinstance(reason, str):
            content = content + reason
        content = (content + ' If you find that this should not be happened,'
                    + ' please contact our systme administrator immediately.')
        message.Message.create(
            send_user = None,
            receive_user = self.user,
            title = title,
            content =  content
        )
    
    def __str__(self):
        return 'Wallet: {full_name}: ${self.balance}'.format(full_name=self.user.get_full_name(), self=self)
