from django.contrib import admin

from .models import *

class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'username', 'given_name', 'family_name', 'email', 'phone_number', 'access_token', 'access_token_expiry_time')

admin.site.register(User, UserAdmin)

admin.site.register(Student)

class TutorAdmin(admin.ModelAdmin):
    list_display = ('user', 'activated', 'university', 'type', 'hourly_rate')
admin.site.register(Tutor, TutorAdmin)
admin.site.register(Company)

admin.site.register(SubjectTag)

admin.site.register(University)
admin.site.register(CourseCode)

class TutorialAdmin(admin.ModelAdmin):
    list_display = ('id', 'student', 'tutor', 'start_time', 'end_time', 'cancelled', 'ended')
admin.site.register(Tutorial, TutorialAdmin)

class UnavailablePeriodAdmin(admin.ModelAdmin):
    list_display = ('id', 'tutor', 'start_time', 'end_time', 'cancelled')
admin.site.register(UnavailablePeriod, UnavailablePeriodAdmin)

admin.site.register(Review)

admin.site.register(Coupon)

class MessageAdmin(admin.ModelAdmin):
    list_display = ('pk', 'send_user', 'receive_user', 'title', 'time', 'read')
admin.site.register(Message, MessageAdmin)

admin.site.register(Wallet)

class TransactionAdmin(admin.ModelAdmin):
    list_display = ('withdraw_wallet', 'deposit_wallet', 'time', 'amount')
admin.site.register(Transaction, TransactionAdmin)
