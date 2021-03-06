import string, random
from datetime import datetime, timezone, timedelta

from django.db import models
from django.contrib.auth.models import User as BaseUser

from . import student, tutor, company, wallet, message

from .. import res

# https://blog.khophi.co/extending-django-user-model-userprofile-like-a-pro/https://blog.khophi.co/extending-django-user-model-userprofile-like-a-pro/

class User(BaseUser):

    @classmethod
    def create(cls, username, password, email, given_name, family_name, phone_number, avatar=None, **kwargs):
        user = cls.objects.create(
            username = username,
            email = email,
            first_name = given_name,
            last_name = family_name,
            phone_number = phone_number
        )
        user.set_password(password)
        if avatar is not None:
            user.avatar = avatar
        user.save()
        wallet.Wallet.create(user=user, **kwargs)
        return user

    base_user = models.OneToOneField(BaseUser, parent_link=True, on_delete=models.CASCADE, related_name='user', related_query_name='user')

    access_token = models.CharField(max_length=128, null=True, blank=True, default=None)

    access_token_expiry_time = models.DateTimeField(null=True, blank=True, default=None)

    phone_number = models.CharField(max_length=8)

    avatar = models.TextField(blank=True, default=res.default_avatar)


    @property
    def given_name(self):
        return self.first_name

    @given_name.setter
    def given_name(self, value):
        self.first_name = value

    @property
    def family_name(self):
        return self.last_name

    @family_name.setter
    def family_name(self, value):
        self.last_name = value

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
    

    def generate_access_token(self):
        self.access_token = ''.join(random.choice(string.digits + string.ascii_lowercase) for i in range(8))
        self.access_token_expiry_time = datetime.now(tz=timezone.utc) + timedelta(hours=1)
        self.save()
        return (self.access_token, self.access_token_expiry_time)


    def send_message(self, to_user, **kwargs):
        return message.Message.create(self, to_user, **kwargs)

    def has_no_event(self, start_time, end_time):
        if end_time < start_time:
            raise ValueError('end_time cannot before start_time')
        events = self.event_set.filter(end_time__gt=start_time, start_time__lt=end_time, cancelled=False)
        return not events.exists()


    def __str__(self):
        return '{self.user.username} ({full_name})'.format(self=self, full_name=self.get_full_name())
