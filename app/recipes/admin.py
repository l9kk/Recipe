from django.contrib import admin
from .models import Recipe, Comment, Like


class CommentInline(admin.TabularInline):
    model = Comment
    extra = 0


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ["title", "author", "status", "created_at", "difficulty", "cooking_time"]
    list_filter = ["status", "created_at", "updated_at", "difficulty"]
    search_fields = ["title", "description", "ingredients", "instructions"]
    prepopulated_fields = {"slug": ("title",)}
    date_hierarchy = "created_at"
    raw_id_fields = ["author"]
    inlines = [CommentInline]
    actions = ["make_published", "make_draft"]
    
    def make_published(self, request, queryset):
        queryset.update(status="published")
    make_published.short_description = "Mark selected recipes as published"
    
    def make_draft(self, request, queryset):
        queryset.update(status="draft")
    make_draft.short_description = "Mark selected recipes as drafts"


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ["author", "recipe", "created_at"]
    list_filter = ["created_at"]
    search_fields = ["text", "author__username", "recipe__title"]
    date_hierarchy = "created_at"
    raw_id_fields = ["author", "recipe"]


@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ["user", "recipe", "created_at"]
    list_filter = ["created_at"]
    date_hierarchy = "created_at"
    raw_id_fields = ["user", "recipe"] 