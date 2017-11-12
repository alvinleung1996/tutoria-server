from decimal import Decimal
from datetime import timedelta

from django.db import models

from . import event, user, tutor, coupon, transaction, wallet, message
coupon_m = coupon

from ..api_exception import ApiException


class Tutorial(event.Event):

    class TutorialNotCreatableError(ApiException):
        def __init__(self, bill):
            self.bill = bill


    @classmethod
    def preview(cls, student, tutor, start_time, end_time, coupon=None, **kwargs):
        """

        """
        # Check if time is valid
        time_is_valid = student.is_valid_tutorial_time(start_time, end_time) and tutor.is_valid_tutorial_time(start_time, end_time)
        # TODO: lock event table to prevent race condition

        if not isinstance(coupon, coupon_m.Coupon):
            try:
                coupon = coupon_m.Coupon.objects.get(code=coupon)
            except coupon_m.Coupon.DoesNotExist:
                coupon = None
        
        coupon_is_valid = False if coupon is None else coupon.is_valid_now()


        tutor_fee = tutor.calc_tutorial_fee(start_time, end_time)

        commission_fee = Decimal('0') if (coupon is not None and coupon_is_valid) else tutor_fee * Decimal('0.05')
        
        coupon_discount =  -commission_fee if (coupon is not None and coupon_is_valid) else Decimal('0')

        total_fee = tutor_fee + commission_fee + coupon_discount


        balance = student.user.wallet.balance

        payable = balance >= total_fee


        creatable = time_is_valid and (coupon is None or coupon_is_valid) and payable


        return dict(
            student = student,
            tutor = tutor,

            start_time = start_time,
            end_time = end_time,
            time_is_valid = time_is_valid,

            tutor_fee = tutor_fee,
            commission_fee = commission_fee,
            coupon_discount = coupon_discount,
            total_fee = total_fee,

            coupon = coupon,
            coupon_is_valid = coupon_is_valid,

            balance = balance,
            payable = payable,

            creatable = creatable
        )
        

    @classmethod
    def create(cls, student, tutor, start_time, end_time, **kwargs):
        """

        """
        preview = cls.preview(student, tutor, start_time, end_time)

        if not preview['creatable']:
            raise cls.TutorialNotCreatableError(bill=bill)

        if preview['total_fee'] > Decimal('0'):
            student_to_company_transaction = transaction.Transaction.create(
                withdraw = student.user,
                deposit = user.User.objects.get(company__isnull=False),
                amount = preview['total_fee']
            )
        else:
            student_to_company_transaction = None

        tutorial = cls.objects.create(
            student = student,
            tutor = tutor,

            start_time = start_time,
            end_time = end_time,

            tutor_fee = preview['tutor_fee'],
            commission_fee = preview['commission_fee'],
            coupon_discount = preview['coupon_discount'],

            coupon = preview['coupon'],

            student_to_company_transaction = student_to_company_transaction
        )
        tutorial.user_set.set([student.user, tutor.user])

        return tutorial


    event = models.OneToOneField('Event', on_delete=models.CASCADE, parent_link=True, related_name='tutorial', related_query_name='tutorial')
    
    student = models.ForeignKey('Student', on_delete=models.PROTECT, related_name='tutorial_set', related_query_name='tutorial')
    tutor = models.ForeignKey('Tutor', on_delete=models.PROTECT, related_name='tutorial_set', related_query_name='tutorial')

    # Need to save the fee because the tutor may change its hourly rate or type at any time
    tutor_fee = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0'))
    commission_fee = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0'))
    coupon_discount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0'))

    coupon = models.ForeignKey('Coupon', related_name='tutorial_set', related_query_name='tutorial', null=True, default=None, blank=True)

    
    student_to_company_transaction = models.OneToOneField('Transaction', on_delete=models.SET_NULL,
                                                          related_name='reason_tutorial_student_to_company',
                                                          related_query_name='reason_tutorial_student_to_company',
                                                          null=True, default=None, blank=True)
    company_to_tutor_transaction = models.OneToOneField('Transaction', on_delete=models.SET_NULL,
                                                        related_name='reason_tutorial_company_to_tutor',
                                                        related_query_name='reason_tutorial_company_to_tutor',
                                                        null=True, default=None, blank=True)
    # Refund
    company_to_student_transaction = models.OneToOneField('Transaction', on_delete=models.SET_NULL,
                                                          related_name='reason_tutorial_company_to_student',
                                                          related_query_name='reason_tutorial_company_to_student',
                                                          null=True, default=None, blank=True)
    
    @property
    def total_fee(self):
        return self.tutor_fee + self.commission_fee + self.coupon_discount

    
    def pay_to_tutor(self):
        if (self.tutor_fee == Decimal('0')):
            return

        if self.company_to_tutor_transaction is not None:
            raise ApiException('Tutorial fee has been paid to tutor')

        self.company_to_tutor_transaction = transaction.Transaction.create(
            withdraw = user.User.objects.get(company__isnull=False),
            deposit = self.tutor.user,
            amount = self.tutor_fee
        )
        self.save()
        

    def refund(self):
        if (self.total_fee == Decimal('0')):
            return

        if self.company_to_tutor_transaction is not None:
            raise ApiException('Tutorial fee has been paid to tutor')
        
        if self.company_to_student_transaction is not None:
            raise ApiException('Tutorial fee has been funded')
        
        self.company_to_student_transaction = transaction.Transaction.create(
            withdraw = user.User.objects.get(company__isnull=False),
            deposit = self.tutor.user,
            amount = self.total_fee
        )
        self.save()


    def __str__(self):
        return 'Tutorial: {self.student} {self.tutor}'.format(self=self)
