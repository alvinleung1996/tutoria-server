from django.db import models
from django.contrib.auth.models import User

# https://blog.khophi.co/extending-django-user-model-userprofile-like-a-pro/https://blog.khophi.co/extending-django-user-model-userprofile-like-a-pro/

class UserProfile(models.Model):

    @classmethod
    def create(cls, username, password, email, givenName, familyName, phoneNumber, avatar=''):
        user = User.objects.create_user(username=username, password=password, email=email, first_name=givenName, last_name=familyName)
        return cls.objects.create(user=user, phoneNumber=phoneNumber, avatar=avatar)
        
    

    user = models.OneToOneField(User, related_name='userProfile', related_query_name='userProfile')

    phoneNumber = models.CharField(max_length=8)

    avatar = models.TextField(blank=True, default='')


    @property
    def username(self):
        return self.user.get_username()

    @username.setter
    def username(self, value):
        self.user.username = value
    
    @property
    def password(self):
        return self.user.password
    
    def setPassword(rawPassword):
        self.user.set_password(rawPassword)

    @property
    def email(self):
        return self.user.email

    @email.setter
    def email(self, value):
        self.user.email = value

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

    @property
    def fullName(self):
        return self.givenName + ' ' + self.familyName


    @property
    def roles(self):
        return self.roleSet.all()

    @property
    def concreteRoles(self):
        result = []
        roles = self.roles
        for role in roles:
            conRole = role.concreteRole
            if conRole is not None:
                result.append(conRole)
        return result

    def getConcreteRole(self, roleType):
        roles = self.roles
        for role in roles:
            concreteRole = role.concreteRole
            if isinstance(concreteRole, roleType):
                return concreteRole
        return None

    def addConcreteRole(self, roleType, *args, **kwargs):
        role = self.getConcreteRole(roleType)
        if role is not None:
            return role
        else:
            return roleType.create(self, *args, **kwargs)
    

    @property
    def occupiedSessions(self):
        return self.occupiedSessionSet.all()
            

    
    def save(self, *args, **kwargs):
        self.user.save()
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        self.user.delete()
        super().delete(*args, **kwargs)

    def __str__(self):
        return '{self.user.username} ({self.givenName} {self.familyName})'.format(self=self)


