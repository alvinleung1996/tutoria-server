from django.db import models
from django.contrib.auth.models import User as BaseUser

# https://blog.khophi.co/extending-django-user-model-userprofile-like-a-pro/https://blog.khophi.co/extending-django-user-model-userprofile-like-a-pro/

class User(BaseUser):

    @classmethod
    def create(cls, username, password, email, givenName, familyName, phoneNumber, avatar=''):
        return cls.objects.create(
            username = username,
            password = password,
            email = email,
            first_name = givenName,
            last_name = familyName, 
            phoneNumber = phoneNumber,
            avatar = avatar
        )

    baseUser = models.OneToOneField(BaseUser, parent_link=True, related_name='user', related_query_name='user')

    phoneNumber = models.CharField(max_length=8)

    avatar = models.TextField(blank=True, default='')


    @property
    def givenName(self):
        return self.user.first_name

    @givenName.setter
    def givenName(self, value):
        self.user.first_name = value

    @property
    def familyName(self):
        return self.user.last_name

    @familyName.setter
    def familyName(self, value):
        self.user.last_name = value



    def addConcreteRole(self, roleType, *args, **kwargs):
        role = self.getConcreteRole(roleType)
        if role is not None:
            return role
        else:
            return roleType.create(self, *args, **kwargs)


    def __str__(self):
        return '{self.user.username} ({self.givenName} {self.familyName})'.format(self=self)
