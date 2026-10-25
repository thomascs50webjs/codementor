from django.db import models
from django.contrib.auth.models import AbstractUser
from typing import Optional
from django.conf import settings
from django.utils.text import slugify

class User(AbstractUser):
    """Custom user model extending Django's AbstractUser."""
    has_agreed_policy = models.BooleanField(default=False)
    
    pass


class Query(models.Model):
    """Model for storing user queries."""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    question = models.TextField(max_length=1000)
    answer = models.TextField(blank=True)
    timeDate = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"{self.user.username} - {self.question[:50]}"
    
    class Meta:
        db_table = 'app_query'


class Favourite(models.Model):
    """Model for storing user favorites."""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    query = models.ForeignKey(Query, on_delete=models.CASCADE)
    timeDate = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"{self.user.username} favorited Query {self.query.id}"
    
    class Meta:
        db_table = 'app_favourite'


class UserTitle(models.Model):
    """Model for storing custom user dashboard titles."""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='custom_title') 
    title = models.CharField(max_length=100)

    def __str__(self) -> str:
        return f"{self.user.username} - {self.title}"
    
    class Meta:
        db_table = 'app_usertitle'


class Pen(models.Model):
    """Model for storing user code pens."""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200, blank=True)
    html_code = models.TextField()
    css_code = models.TextField(blank=True)
    js_code = models.TextField(blank=True)
    extra_files = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_draft = models.BooleanField(default=True)
    views = models.IntegerField(default=0)
    is_fork = models.BooleanField(default=False)
    is_edited = models.BooleanField(default=False)

    def __str__(self) :
        return f"{self.title} by {self.user.username}"

    @property
    def slug(self):
        return slugify(self.title) if self.title else 'untitled'
    
    class Meta:
        db_table = 'app_pen'


class OnboardingResponse(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='onboarding')
    question_one = models.CharField(max_length=200, blank=True)
    question_two = models.CharField(max_length=200, blank=True)
    current_step = models.IntegerField(default=1)
    completed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        # self.user is a User instance on model objects
        return f"Onboarding for {self.user.username}: {self.question_one}, {self.question_two}"


class ContactMessage(models.Model):
    full_name = models.CharField(max_length=255)
    subject = models.CharField(max_length=255)
    message = models.TextField()
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.full_name} - {self.subject}"

        
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_picture = models.ImageField(
        upload_to='profile_pics/',
        default='default-avatar.png',
        null=True,
        blank=True
    )

    def __str__(self):
        return self.user.username