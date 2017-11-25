from decimal import Decimal
from datetime import datetime, timedelta

from django.db import models
from django.utils import timezone as djtimezone

from . import event, user, tutor, coupon, transaction, wallet, message
coupon_m = coupon

from ..api_exception import ApiException


class Tutorial(event.Event):

    class TutorialNotCreatableError(ApiException):
        def __init__(self, preview):
            self.preview = preview


    @classmethod
    def preview(cls, student, tutor, start_time, end_time, coupon=None, **kwargs):
        """

        """
        # Check if time is valid
        time_valid = student.is_valid_tutorial_time(start_time, end_time) and tutor.is_valid_tutorial_time(start_time, end_time)
        # TODO: lock event table to prevent race condition

        # Student cannot book the same tutor at the same day
        if time_valid:

            local_day_start_time = start_time.astimezone(djtimezone.get_current_timezone()).replace(
                hour = 0, minute = 0, second = 0, microsecond = 0
            )
            local_day_end_time = local_day_start_time + timedelta(days=1)

            # if student has already book one tutorial on the sam day
            time_valid = not cls.objects.filter(
                start_time__lt = local_day_end_time,
                end_time__gt = local_day_start_time,
                student = student,
                tutor = tutor,
                cancelled = False,
            ).exists()


        if coupon is None:
            coupon_valid = None
        elif isinstance(coupon, coupon_m.Coupon):
            coupon_valid = coupon.is_valid_now()
        else:
            try:
                coupon = coupon_m.Coupon.objects.get(code=coupon)
                coupon_valid = coupon.is_valid_now()
            except coupon_m.Coupon.DoesNotExist:
                coupon = None
                coupon_valid = False


        tutor_fee = tutor.calc_tutorial_fee(start_time, end_time)

        commission_fee = tutor_fee * Decimal('0.05')
        
        coupon_discount =  -commission_fee if coupon_valid else Decimal('0')

        total_fee = tutor_fee + commission_fee + coupon_discount


        balance = student.user.wallet.balance

        is_payable = balance >= total_fee


        creatable = time_valid and (coupon_valid is None or coupon_valid is True) and is_payable


        return dict(
            student = student,
            tutor = tutor,

            start_time = start_time,
            end_time = end_time,
            time_valid = time_valid,

            tutor_fee = tutor_fee,
            commission_fee = commission_fee,
            coupon_discount = coupon_discount,
            total_fee = total_fee,

            coupon = coupon,
            coupon_valid = coupon_valid,

            balance = balance,
            is_payable = is_payable,

            creatable = creatable
        )
        

    @classmethod
    def create(cls, student, tutor, start_time, end_time, coupon=None, **kwargs):
        """

        """
        preview = cls.preview(
            student = student,
            tutor = tutor,
            start_time = start_time,
            end_time = end_time,
            coupon = coupon
        )

        if not preview['creatable']:
            raise cls.TutorialNotCreatableError(preview=preview)

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

        title = 'New tutorial booking'
        content = (
            'A new student has booked a tutorial session of yours.\n'
            'Name: ' + student.user.full_name + '\n' +
            'Phone number: ' + student.user.phone_number + '\n'
        )

        message.Message.create(
            send_user = None,
            receive_user = tutor.user,
            title = 'New tutorial booking',
            content = content
        )

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
    
    ended = models.BooleanField(default=False)
    
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
        

    @property
    def cancellable(self):
        if self.cancelled:
            return False

        return (self.start_time - datetime.now(tz=djtimezone.get_default_timezone())) >= timedelta(days=1)
    

    def cancel(self):
        if (self.start_time - datetime.now(tz=djtimezone.get_default_timezone())) < timedelta(days=1):
            raise ApiException(message='Cannot cancel tutorial within 24hrs before its start time')
        
        if (self.total_fee > Decimal('0')):

            if self.company_to_tutor_transaction is not None:
                raise ApiException(message='Tutorial fee has already been paid to tutor')
            
            if self.company_to_student_transaction is not None:
                raise ApiException(message='Tutorial fee has already been funded')

            self.company_to_student_transaction = transaction.Transaction.create(
                withdraw = user.User.objects.get(company__isnull=False),
                deposit = self.student.user,
                amount = self.total_fee
            )
        
        self.cancelled = True

        self.save()

        message.Message.create(
            send_user = None,
            receive_user = self.student.user,
            title = 'Booking cancelled',
            content = 'Your booking with ' + self.tutor.user.full_name + ' from '+ str(self.start_time) + ' to ' + str(self.end_time) + ' has already been cancelled.'
            # TODO: update message content and title
        )

        message.Message.create(
            send_user = None,
            receive_user = self.tutor.user,
            title = 'Booking cancelled',
            content = 'Your booking with ' + self.student.user.full_name + ' from '+ str(self.start_time) + ' to ' + str(self.end_time) + ' has already been cancelled.'
            # TODO: update message content and title
        )


    def __str__(self):
        return 'Tutorial: {self.student} {self.tutor}'.format(self=self)
