from django.db import models



class CourseCode(models.Model):

    @classmethod
    def create(cls, code):
        return cls.objects.create(code=code)

    code = models.CharField(max_length=10)

    @property
    def tutorRoles(self):
        return self.tutorRoleSet.all()

    def __str__(self):
        return 'CourseCode: "{self.code}"'.format(self=self)
