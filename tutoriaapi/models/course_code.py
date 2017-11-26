from django.db import models

class CourseCode(models.Model):

    @classmethod
    def create(cls, university, code):
        return cls.objects.create(
            university = university,
            code=code
        )
    
    university = models.ForeignKey('University', on_delete=models.CASCADE, related_name='course_code_set', related_query_name='course_code')
    
    code = models.CharField(max_length=10)

    def __str__(self):
        return 'CourseCode: "{self.code}"'.format(self=self)
