from django.urls import path
from . import views

urlpatterns = [
    path("<str:username>/", views.UserDetailView.as_view(), name="user_detail"),
    path("profile/edit/", views.UserUpdateView.as_view(), name="profile_edit"),
    path("<str:username>/recipes/", views.UserRecipeListView.as_view(), name="user_recipes"),
    path("<str:username>/favorites/", views.UserFavoriteRecipeListView.as_view(), name="user_favorites"),
    path("recipe/<int:recipe_id>/favorite/", views.toggle_favorite, name="toggle_favorite"),
] 