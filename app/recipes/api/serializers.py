from rest_framework import serializers
from taggit.serializers import TagListSerializerField, TaggitSerializer
from django.contrib.auth import get_user_model
from recipes.models import Recipe, Comment, Like


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ["id", "username", "first_name", "last_name"]


class CommentSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    
    class Meta:
        model = Comment
        fields = ["id", "author", "text", "created_at"]


class RecipeSerializer(TaggitSerializer, serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    tags = TagListSerializerField()
    likes_count = serializers.IntegerField(source="total_likes", read_only=True)
    comments_count = serializers.IntegerField(source="total_comments", read_only=True)
    is_liked = serializers.SerializerMethodField()
    
    class Meta:
        model = Recipe
        fields = [
            "id", "title", "slug", "author", "description", "ingredients", 
            "instructions", "cooking_time", "servings", "difficulty", 
            "image", "created_at", "updated_at", "tags", "likes_count", 
            "comments_count", "is_liked"
        ]
        read_only_fields = ["id", "slug", "created_at", "updated_at"]
    
    def get_is_liked(self, obj):
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            return Like.objects.filter(recipe=obj, user=request.user).exists()
        return False


class RecipeCreateUpdateSerializer(TaggitSerializer, serializers.ModelSerializer):
    tags = TagListSerializerField()
    
    class Meta:
        model = Recipe
        fields = [
            "title", "description", "ingredients", "instructions", 
            "cooking_time", "servings", "difficulty", "image", "tags", "status"
        ]
    
    def create(self, validated_data):
        validated_data["author"] = self.context["request"].user
        return super().create(validated_data) 