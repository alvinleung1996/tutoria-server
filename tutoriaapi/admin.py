from django.contrib import admin

from .models import *

class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'givenName', 'familyName', 'phoneNumber')

admin.site.register(UserProfile, UserProfileAdmin)

admin.site.register(StudentRole)
admin.site.register(TutorRole)

admin.site.register(University)
admin.site.register(CourseCode)

admin.site.register(TutorialSession)
admin.site.register(BlackenOutSession)
