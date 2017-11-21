from django.db import models

class Company(models.Model):

    @classmethod
    def create(cls, user):
        if cls.objects.all().count() > 0:
            raise Exception('Cannot have more than one company role')
        return cls.objects.create(user=user)

    user = models.OneToOneField('User', on_delete=models.CASCADE, related_name='company', related_query_name='company')

    def __str__(self):
        return 'Company: {self.user.given_name} {self.user.family_name}'.format(self=self)
