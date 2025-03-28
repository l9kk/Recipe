from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import DetailView, UpdateView, ListView
from django.contrib import messages
from .models import CustomUser
from .forms import ProfileUpdateForm
from recipes.models import Recipe


class UserDetailView(DetailView):
    model = CustomUser
    template_name = "users/user_detail.html"
    context_object_name = "user_profile"
    slug_field = "username"
    slug_url_kwarg = "username"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.get_object()
        context["recipes"] = Recipe.objects.filter(author=user).order_by("-created_at")[:5]
        context["favorite_recipes"] = user.favorite_recipes.all()[:5]
        return context


class UserUpdateView(LoginRequiredMixin, UpdateView):
    model = CustomUser
    form_class = ProfileUpdateForm
    template_name = "users/user_update.html"
    
    def get_object(self):
        return self.request.user
    
    def get_success_url(self):
        messages.success(self.request, "Your profile has been updated!")
        return reverse_lazy("user_detail", kwargs={"username": self.request.user.username})


class UserRecipeListView(ListView):
    model = Recipe
    template_name = "users/user_recipes.html"
    context_object_name = "recipes"
    paginate_by = 10
    
    def get_queryset(self):
        self.user = get_object_or_404(CustomUser, username=self.kwargs.get("username"))
        return Recipe.objects.filter(author=self.user).order_by("-created_at")
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["user_profile"] = self.user
        return context


class UserFavoriteRecipeListView(ListView):
    model = Recipe
    template_name = "users/user_favorites.html"
    context_object_name = "recipes"
    paginate_by = 10
    
    def get_queryset(self):
        self.user = get_object_or_404(CustomUser, username=self.kwargs.get("username"))
        return self.user.favorite_recipes.all().order_by("-created_at")
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["user_profile"] = self.user
        return context


@login_required
def toggle_favorite(request, recipe_id):
    recipe = get_object_or_404(Recipe, id=recipe_id)
    user = request.user
    
    if recipe in user.favorite_recipes.all():
        user.favorite_recipes.remove(recipe)
        messages.info(request, f"'{recipe.title}' removed from favorites")
    else:
        user.favorite_recipes.add(recipe)
        messages.success(request, f"'{recipe.title}' added to favorites")
    
    next_url = request.POST.get("next", request.META.get("HTTP_REFERER", "home"))
    return redirect(next_url) 