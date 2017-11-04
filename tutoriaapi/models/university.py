from django.db import models

class University(models.Model):

    @classmethod
    def create(cls, name):
        return cls.objects.create(name=name)

    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return 'University: "{self.name}"'.format(self=self)
