from django.contrib import admin

from .models import *

class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'given_name', 'family_name', 'phone_number')

admin.site.register(User, UserAdmin)

admin.site.register(Student)

class TutorAdmin(admin.ModelAdmin):
    list_display = ('id', 'user')
admin.site.register(Tutor, TutorAdmin)

admin.site.register(SubjectTag)

admin.site.register(University)
admin.site.register(CourseCode)

class TutorialAdmin(admin.ModelAdmin):
    list_display = ('id', 'student', 'tutor', 'start_date', 'end_date', 'locked', 'cancelled')
admin.site.register(Tutorial, TutorialAdmin)

class UnavailablePeriodAdmin(admin.ModelAdmin):
    list_display = ('id', 'tutor', 'start_date', 'end_date', 'cancelled')
admin.site.register(UnavailablePeriod, UnavailablePeriodAdmin)

admin.site.register(Review)
