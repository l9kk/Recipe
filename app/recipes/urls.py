from django.urls import path
from . import views

urlpatterns = [
    path("", views.RecipeListView.as_view(), name="recipe_list"),
    path("create/", views.RecipeCreateView.as_view(), name="recipe_create"),
    path("<slug:slug>/", views.RecipeDetailView.as_view(), name="recipe_detail"),
    path("<slug:slug>/edit/", views.RecipeUpdateView.as_view(), name="recipe_update"),
    path("<slug:slug>/delete/", views.RecipeDeleteView.as_view(), name="recipe_delete"),
    path("<slug:slug>/comment/", views.add_comment, name="add_comment"),
    path("comment/<int:comment_id>/delete/", views.delete_comment, name="delete_comment"),
    path("<int:recipe_id>/like/", views.toggle_like, name="toggle_like"),
    path("tag/<slug:tag_slug>/", views.tag_recipes, name="tag_recipes"),
    path("my/drafts/", views.UserDraftListView.as_view(), name="user_drafts"),
    path("<slug:slug>/publish/", views.publish_recipe, name="publish_recipe"),
] 