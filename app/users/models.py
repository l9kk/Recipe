from django.contrib.auth.models import AbstractUser
from django.db import models
from django.urls import reverse


class CustomUser(AbstractUser):
    bio = models.TextField(blank=True)
    profile_picture = models.ImageField(upload_to="profile_pics", blank=True, null=True)
    favorite_recipes = models.ManyToManyField(
        "recipes.Recipe", related_name="favorited_by", blank=True
    )
    
    def __str__(self):
        return self.username
    
    def get_absolute_url(self):
        return reverse("user_detail", kwargs={"username": self.username}) 