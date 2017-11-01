from django.contrib import admin

from .models import *

class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'givenName', 'familyName', 'phoneNumber')

admin.site.register(User, UserAdmin)

admin.site.register(Student)

class TutorAdmin(admin.ModelAdmin):
    list_display = ('id', 'user')
admin.site.register(Tutor, TutorAdmin)

admin.site.register(SubjectTag)

admin.site.register(University)
admin.site.register(CourseCode)

class TutorialAdmin(admin.ModelAdmin):
    list_display = ('id', 'student', 'tutor', 'startDate', 'endDate', 'locked', 'cancelled')
admin.site.register(Tutorial, TutorialAdmin)

class UnavailablePeriodAdmin(admin.ModelAdmin):
    list_display = ('id', 'tutor', 'startDate', 'endDate', 'cancelled')
admin.site.register(UnavailablePeriod, UnavailablePeriodAdmin)

admin.site.register(Review)
