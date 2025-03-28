from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required
from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, DeleteView
)
from django.contrib import messages
from django.db.models import Q
from django.http import JsonResponse
from taggit.models import Tag
from .models import Recipe, Comment, Like
from .forms import RecipeForm, CommentForm, RecipeSearchForm


class RecipeListView(ListView):
    model = Recipe
    template_name = "recipes/recipe_list.html"
    context_object_name = "recipes"
    paginate_by = 9
    
    def get_queryset(self):
        queryset = Recipe.objects.filter(status="published")
        form = RecipeSearchForm(self.request.GET)
        
        if form.is_valid():
            query = form.cleaned_data["query"]
            difficulty = form.cleaned_data["difficulty"]
            max_cooking_time = form.cleaned_data["max_cooking_time"]
            tags = form.cleaned_data["tags"]
            
            if query:
                queryset = queryset.filter(
                    Q(title__icontains=query) | 
                    Q(description__icontains=query) |
                    Q(ingredients__icontains=query)
                )
            
            if difficulty:
                queryset = queryset.filter(difficulty=difficulty)
            
            if max_cooking_time:
                queryset = queryset.filter(cooking_time__lte=max_cooking_time)
            
            if tags:
                tag_list = [tag.strip() for tag in tags.split(",")]
                queryset = queryset.filter(tags__name__in=tag_list).distinct()
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = RecipeSearchForm(self.request.GET)
        context["tags"] = Tag.objects.all()[:20]
        return context


class RecipeDetailView(DetailView):
    model = Recipe
    template_name = "recipes/recipe_detail.html"
    context_object_name = "recipe"
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # If the user is the author, show the recipe even if it's a draft
        if self.request.user.is_authenticated:
            return queryset.filter(
                Q(status="published") | Q(author=self.request.user)
            )
        
        return queryset.filter(status="published")
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["comment_form"] = CommentForm()
        context["user_liked"] = False
        
        if self.request.user.is_authenticated:
            recipe = self.get_object()
            context["user_liked"] = Like.objects.filter(
                recipe=recipe, user=self.request.user
            ).exists()
        
        return context


class RecipeCreateView(LoginRequiredMixin, CreateView):
    model = Recipe
    form_class = RecipeForm
    template_name = "recipes/recipe_form.html"
    
    def form_valid(self, form):
        form.instance.author = self.request.user
        messages.success(self.request, "Recipe created successfully!")
        return super().form_valid(form)


class RecipeUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Recipe
    form_class = RecipeForm
    template_name = "recipes/recipe_form.html"
    
    def test_func(self):
        recipe = self.get_object()
        return self.request.user == recipe.author
    
    def form_valid(self, form):
        messages.success(self.request, "Recipe updated successfully!")
        return super().form_valid(form)


class RecipeDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Recipe
    template_name = "recipes/recipe_confirm_delete.html"
    success_url = reverse_lazy("recipe_list")
    
    def test_func(self):
        recipe = self.get_object()
        return self.request.user == recipe.author
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, "Recipe deleted successfully!")
        return super().delete(request, *args, **kwargs)


@login_required
def add_comment(request, slug):
    recipe = get_object_or_404(Recipe, slug=slug)
    
    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.recipe = recipe
            comment.author = request.user
            comment.save()
            messages.success(request, "Comment added successfully!")
            return redirect("recipe_detail", slug=slug)
    
    return redirect("recipe_detail", slug=slug)


@login_required
def delete_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    
    if request.user == comment.author:
        recipe_slug = comment.recipe.slug
        comment.delete()
        messages.success(request, "Comment deleted!")
        return redirect("recipe_detail", slug=recipe_slug)
    
    messages.error(request, "You don't have permission to delete this comment!")
    return redirect("recipe_detail", slug=comment.recipe.slug)


@login_required
def toggle_like(request, recipe_id):
    recipe = get_object_or_404(Recipe, id=recipe_id)
    user = request.user
    like, created = Like.objects.get_or_create(recipe=recipe, user=user)
    
    if not created:
        like.delete()
        liked = False
    else:
        liked = True
    
    if request.is_ajax():
        return JsonResponse({
            "liked": liked,
            "total_likes": recipe.total_likes
        })
    
    return redirect("recipe_detail", slug=recipe.slug)


def tag_recipes(request, tag_slug):
    tag = get_object_or_404(Tag, slug=tag_slug)
    recipes = Recipe.objects.filter(status="published", tags__in=[tag])
    
    return render(request, "recipes/tag_recipes.html", {
        "tag": tag,
        "recipes": recipes
    })


class UserDraftListView(LoginRequiredMixin, ListView):
    model = Recipe
    template_name = "recipes/user_drafts.html"
    context_object_name = "recipes"
    paginate_by = 10
    
    def get_queryset(self):
        return Recipe.objects.filter(author=self.request.user, status="draft").order_by("-created_at")


@login_required
def publish_recipe(request, slug):
    recipe = get_object_or_404(Recipe, slug=slug, author=request.user)
    recipe.status = "published"
    recipe.save()
    messages.success(request, f"'{recipe.title}' published successfully!")
    return redirect("recipe_detail", slug=slug) 