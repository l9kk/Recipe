from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser
from .forms import CustomUserCreationForm, CustomUserChangeForm


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = CustomUser
    list_display = ["username", "email", "first_name", "last_name", "is_staff"]
    fieldsets = UserAdmin.fieldsets + (
        ("Profile", {"fields": ("bio", "profile_picture", "favorite_recipes")}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ("Profile", {"fields": ("bio", "profile_picture")}),
    ) 