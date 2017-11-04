from decimal import Decimal
from datetime import timedelta

from django.db import models

from . import event, user, tutor, coupon, transaction, wallet
tutor_m = tutor

from ..api_exception import ApiException


class Tutorial(event.Event):

    class TimeNotAvailableError(ApiException):
        pass
    
    class InvalidStartTimeError(ApiException):
        pass
    
    class InvalidTimeError(ApiException):
        pass


    @classmethod
    def preview(cls, student, tutor, start_time, end_time, **kwargs):
        

        if (not student.is_valid_tutorial_time(start_time, end_time)
                or not tutor.is_valid_tutorial_time(start_time, end_time)):
            raise cls.TimeNotAvailableError()
        # TODO: lock event table to prevent race condition

        fee = tutor.calc_tutorial_fee(start_time, end_time)
        
        return dict(
            student = student,
            tutor = tutor,
            start_time = start_time,
            end_time = end_time,
            fee = fee,
            payable = bool(student.user.wallet.balance >= fee)
        )
        

    @classmethod
    def create(cls, student, tutor, start_time, end_time, **kwargs):
        preview = cls.preview(student, tutor, start_time, end_time)
        if not preview['payable']:
            raise wallet.Wallet.InsufficientBalanceError()
        
        fee = preview['fee']

        student_to_company_transaction = transaction.Transaction.create(
            withdraw = student.user,
            deposit = user.User.objects.get(company__isnull=False),
            amount = fee
        )

        tutorial = cls.objects.create(
            start_time = start_time,
            end_time = end_time,
            student = student,
            tutor = tutor,
            fee = fee,
            student_to_company_transaction = student_to_company_transaction
        )
        tutorial.user_set.set([student.user, tutor.user])

        return tutorial




    event = models.OneToOneField('Event', on_delete=models.CASCADE, parent_link=True, related_name='tutorial', related_query_name='tutorial')
    
    student = models.ForeignKey('Student', on_delete=models.PROTECT, related_name='tutorial_set', related_query_name='tutorial')
    tutor = models.ForeignKey('Tutor', on_delete=models.PROTECT, related_name='tutorial_set', related_query_name='tutorial')

    # Need to save the fee because the tutor may change its hourly rate or type at any time
    fee = models.DecimalField(max_digits=12, decimal_places=2)
    coupon = models.ManyToManyField(coupon.Coupon, related_name='tutorial_set', related_query_name='tutorial')

    
    student_to_company_transaction = models.OneToOneField('Transaction', on_delete=models.SET_NULL,
                                                          related_name='reason_tutorial_student_to_company',
                                                          related_query_name='reason_tutorial_student_to_company',
                                                          null=True, default=None)
    company_to_tutor_transaction = models.OneToOneField('Transaction', on_delete=models.SET_NULL,
                                                        related_name='reason_tutorial_company_to_tutor',
                                                        related_query_name='reason_tutorial_company_to_tutor',
                                                        null=True, default=None)
    # Refund
    company_to_student_transaction = models.OneToOneField('Transaction', on_delete=models.SET_NULL,
                                                          related_name='reason_tutorial_company_to_student',
                                                          related_query_name='reason_tutorial_company_to_student',
                                                          null=True, default=None)
    def pay_to_tutor(self):
        if (self.fee == Decimal('0')):
            return
        charge = self.fee / Decimal('1.05')
        self.company_to_tutor_transaction = transaction.Transaction.create(
            withdraw_user = user.User.objects.get(company__isnull=False),
            deposit_user = self.tutor.user,
            amount = charge
        )
    
    def refund(self):
        if (self.fee == Decimal('0')):
            return
        charge = self.fee / Decimal('1.05')
        self.company_to_student_transaction = transaction.Transaction.create(
            withdraw_user = user.User.objects.get(company__isnull=False),
            deposit_user = self.tutor.user,
            amount = charge
        )


    def __str__(self):
        return 'Tutorial: {self.student} {self.tutor}'.format(self=self)
