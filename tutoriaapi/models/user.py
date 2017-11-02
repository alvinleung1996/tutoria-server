from django.db import models
from django.contrib.auth.models import User as BaseUser

# https://blog.khophi.co/extending-django-user-model-userprofile-like-a-pro/https://blog.khophi.co/extending-django-user-model-userprofile-like-a-pro/

class User(BaseUser):

    @classmethod
    def create(cls, username, password, email, given_name, family_name, phone_number, avatar=''):
        return cls.objects.create(
            username = username,
            password = password,
            email = email,
            first_name = given_name,
            last_name = family_name, 
            phone_number = phone_number,
            avatar = avatar
        )

    base_user = models.OneToOneField(BaseUser, parent_link=True, related_name='user', related_query_name='user')

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



    def add_concrete_role(self, role_type, *args, **kwargs):
        role = self.get_concrete_role(role_type)
        if role is not None:
            return role
        else:
            return role_type.create(self, *args, **kwargs)


    def __str__(self):
        return '{self.user.username} ({full_name})'.format(self=self, full_name=self.get_full_name())
