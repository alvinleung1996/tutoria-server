from django.db import models
from django.contrib.auth.models import User as BaseUser
from django.contrib.auth import authenticate,login
from django.core.mail import send_mail, BadHeaderError
from django.http import HttpResponse, HttpResponseRedirect

from . import student, tutor, company, wallet, message
import random

# https://blog.khophi.co/extending-django-user-model-userprofile-like-a-pro/https://blog.khophi.co/extending-django-user-model-userprofile-like-a-pro/

class User(BaseUser):

    @classmethod
    def create(cls, username, password, email, given_name, family_name, phone_number, avatar='', **kwargs):
        user = cls.objects.create(
            username = username,
            email = email,
            first_name = given_name,
            last_name = family_name,
            phone_number = phone_number,
            avatar = avatar
        )
        user.set_password(password)
        user.save()
        wallet.Wallet.create(user=user, **kwargs)
        return user

    base_user = models.OneToOneField(BaseUser, parent_link=True, on_delete=models.CASCADE, related_name='user', related_query_name='user')

    phone_number = models.CharField(max_length=8)

    avatar = models.TextField(blank=True, default='')


    @property
    def given_name(self):
        return self.user.first_name

    @given_name.setter
    def given_name(self, value):
        self.user.first_name = value

    @property
    def family_name(self):
        return self.user.last_name

    @family_name.setter
    def family_name(self, value):
        self.user.last_name = value

    @property
    def full_name(self):
        return self.get_full_name()


    @property
    def roles(self):
        return list(filter(lambda r: r is not None, map(lambda r: self.get_role(r), [student.Student, tutor.Tutor, company.Company])))

    def get_role(self, role_type):
        if role_type is student.Student and hasattr(self, 'student'):
            return self.student
        elif role_type is tutor.Tutor and hasattr(self, 'tutor'):
            return self.tutor
        elif role_type is company.Company and hasattr(self, 'company'):
            return self.company
        else:
            return None

    #as student and tutor
    def add_role(self, role_type, *args, **kwargs):
        role = self.get_role(role_type)
        if role is not None:
            return role
        
        if role_type is student.Student:
            self.student = student.Student.create(user=self, *args, **kwargs)
            return self.student
        elif role_type is tutor.Tutor:
            self.tutor = tutor.Tutor.create(user=self, *args, **kwargs)
            return self.tutor
        elif role_type is company.Company:
            self.company = company.Company.create(user=self, *args, **kwargs)
            return self.company
        else:
            raise Exception('Unsupported role type')

    def send_message(self, to_user, **kwargs):
        return message.Message.create(self, to_user, **kwargs)

    def has_no_event(self, start_time, end_time):
        if end_time < start_time:
            raise ValueError('end_time cannot before start_time')
        events = self.event_set.filter(end_time__gt=start_time, start_time__lt=end_time, cancelled=False)
        return not events.exists()

    def login(request):
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
        else:
            raise Exception('login invalid')
    # then Administrator get the message, and send the mail to user's email
    def request_password_change(request):
        username=request.POST.get('username')
        user_email=request.POST.get('user_email')
        num=random.randint(0,10000)
        subject="Password Reset"
        message="Token num for password reset is"+num
        if username and user_email:
            try:
                send_mail(subject, message, ['cxyang15@connect.hku.hk'], [user_email])
            except BadHeaderError:
                raise Exception('Invalid header found.')
        else:
            raise Exception('Make sure all fields are entered and valid.')








    def __str__(self):
        return '{self.user.username} ({full_name})'.format(self=self, full_name=self.get_full_name())
