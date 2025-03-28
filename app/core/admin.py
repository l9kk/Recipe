from django.contrib.admin import AdminSite
from django.utils.translation import gettext_lazy as _
from django.contrib.admin.apps import AdminConfig


class RecipeAdminSite(AdminSite):
    site_title = _('Recipe Admin')
    site_header = _('Recipe Management')
    index_title = _('Recipe Administration')
    
    index_template = 'admin/custom_index.html'
    app_index_template = 'admin/custom_app_index.html'
    
    def each_context(self, request):
        context = super().each_context(request)
        context['extra_css'] = ['admin/css/custom_admin.css']
        from recipes.models import Recipe
        context['total_recipes'] = Recipe.objects.count()
        context['published_recipes'] = Recipe.objects.filter(status="published").count()
        context['draft_recipes'] = Recipe.objects.filter(status="draft").count()
        return context


recipe_admin_site = RecipeAdminSite(name='recipe_admin')


class RecipeAdminConfig(AdminConfig):
    default_site = 'core.admin.RecipeAdminSite'