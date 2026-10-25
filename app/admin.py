from django.contrib import admin
from .models import Favourite, Query, User, UserTitle, Pen, OnboardingResponse, ContactMessage


admin.site.register(Favourite)
admin.site.register(Query)
admin.site.register(User)
admin.site.register(UserTitle)
admin.site.register(Pen)
@admin.register(OnboardingResponse)
class OnboardingResponseAdmin(admin.ModelAdmin):
    list_display = ('user', 'question_one', 'question_two', 'completed_at')
    search_fields = ('user__username', 'question_one', 'question_two')

@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'subject', 'submitted_at')
    search_fields = ('full_name', 'subject')



# Register your models here.
