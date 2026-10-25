from django.db import models
from django.contrib.auth.models import AbstractUser
from typing import Optional


class User(AbstractUser):
    """Custom user model extending Django's AbstractUser."""
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
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_draft = models.BooleanField(default=True)

    def __str__(self) :
        return f"{self.title} by {self.user.username}"
    
    class Meta:
        db_table = 'app_pen'


