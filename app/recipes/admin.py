from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.contrib import messages
from django.db.models import Count
from django.utils import timezone

from core.admin import recipe_admin_site
from .models import Recipe, Comment, Like


class CommentInline(admin.TabularInline):
    model = Comment
    extra = 0
    readonly_fields = ['created_at']
    fields = ['author', 'text', 'created_at']


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ["title", "author", "display_status", "created_at", "difficulty", 
                    "cooking_time", "likes_count", "comments_count", "view_on_site"]
    list_filter = ["status", "created_at", "updated_at", "difficulty"]
    search_fields = ["title", "description", "ingredients", "instructions"]
    prepopulated_fields = {"slug": ("title",)}
    date_hierarchy = "created_at"
    raw_id_fields = ["author"]
    inlines = [CommentInline]
    actions = ["make_published", "make_draft", "duplicate_recipe", "reset_likes"]
    readonly_fields = ["created_at", "updated_at", "get_likes", "get_comments"]
    fieldsets = (
        (None, {
            'fields': ('title', 'slug', 'author', 'status')
        }),
        ('Content', {
            'fields': ('description', 'ingredients', 'instructions', 'image')
        }),
        ('Recipe Details', {
            'fields': ('cooking_time', 'servings', 'difficulty', 'tags')
        }),
        ('Metadata', {
            'classes': ('collapse',),
            'fields': ('created_at', 'updated_at'),
        }),
        ('Statistics', {
            'fields': ('get_likes', 'get_comments'),
        }),
    )
    list_per_page = 20
    
    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.annotate(
            _likes_count=Count('likes', distinct=True),
            _comments_count=Count('comments', distinct=True)
        )
        return queryset
    
    def likes_count(self, obj):
        return obj._likes_count
    likes_count.admin_order_field = '_likes_count'
    likes_count.short_description = 'Likes'
    
    def comments_count(self, obj):
        return obj._comments_count
    comments_count.admin_order_field = '_comments_count'
    comments_count.short_description = 'Comments'
    
    def display_status(self, obj):
        if obj.status == 'published':
            return format_html('<span class="recipe-status-published">Published</span>')
        else:
            return format_html('<span class="recipe-status-draft">Draft</span>')
    display_status.short_description = 'Status'
    
    def get_likes(self, obj):
        return f"{obj.likes.count()} likes from {obj.likes.values('user').distinct().count()} unique users"
    get_likes.short_description = "Likes Information"
    
    def get_comments(self, obj):
        return f"{obj.comments.count()} comments from {obj.comments.values('author').distinct().count()} unique users"
    get_comments.short_description = "Comments Information"
    
    def view_on_site(self, obj):
        url = reverse('recipe_detail', kwargs={'slug': obj.slug})
        return format_html('<a href="{}" class="button" target="_blank">View Recipe</a>', url)
    view_on_site.short_description = 'View'
    
    def make_published(self, request, queryset):
        updated = queryset.update(status="published")
        messages.success(request, f"{updated} recipe(s) marked as published.")
    make_published.short_description = "Mark selected recipes as published"
    
    def make_draft(self, request, queryset):
        updated = queryset.update(status="draft")
        messages.success(request, f"{updated} recipe(s) marked as drafts.")
    make_draft.short_description = "Mark selected recipes as drafts"
    
    def duplicate_recipe(self, request, queryset):
        for recipe in queryset:
            recipe.pk = None
            recipe.title = f"Copy of {recipe.title}"
            recipe.slug = f"copy-of-{recipe.slug}-{timezone.now().strftime('%Y%m%d%H%M%S')}"
            recipe.status = "draft"
            recipe.created_at = timezone.now()
            recipe.updated_at = timezone.now()
            recipe.save()
            
            # Copy tags
            for tag in recipe.tags.all():
                recipe.tags.add(tag)
                
        messages.success(request, f"{queryset.count()} recipe(s) duplicated successfully.")
    duplicate_recipe.short_description = "Duplicate selected recipes"
    
    def reset_likes(self, request, queryset):
        for recipe in queryset:
            recipe.likes.all().delete()
        messages.success(request, f"Likes reset for {queryset.count()} recipe(s).")
    reset_likes.short_description = "Reset likes for selected recipes"


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ["author", "recipe_link", "text_preview", "created_at"]
    list_filter = ["created_at"]
    search_fields = ["text", "author__username", "recipe__title"]
    date_hierarchy = "created_at"
    raw_id_fields = ["author", "recipe"]
    
    def text_preview(self, obj):
        return obj.text[:50] + "..." if len(obj.text) > 50 else obj.text
    text_preview.short_description = "Comment"
    
    def recipe_link(self, obj):
        url = reverse('admin:recipes_recipe_change', args=[obj.recipe.id])
        return format_html('<a href="{}">{}</a>', url, obj.recipe.title)
    recipe_link.short_description = "Recipe"


@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ["user", "recipe_link", "created_at"]
    list_filter = ["created_at"]
    date_hierarchy = "created_at"
    raw_id_fields = ["user", "recipe"]
    
    def recipe_link(self, obj):
        url = reverse('admin:recipes_recipe_change', args=[obj.recipe.id])
        return format_html('<a href="{}">{}</a>', url, obj.recipe.title)
    recipe_link.short_description = "Recipe"


# Register models with custom admin site
recipe_admin_site.register(Recipe, RecipeAdmin)
recipe_admin_site.register(Comment, CommentAdmin)
recipe_admin_site.register(Like, LikeAdmin)