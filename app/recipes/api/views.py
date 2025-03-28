from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from recipes.models import Recipe, Comment, Like
from .serializers import RecipeSerializer, CommentSerializer, RecipeCreateUpdateSerializer


class IsAuthorOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow authors of an object to edit it.
    """
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed for any request
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write permissions are only allowed to the author
        return obj.author == request.user


class RecipeViewSet(viewsets.ModelViewSet):
    """
    API endpoint for recipes.
    """
    queryset = Recipe.objects.filter(status="published")
    serializer_class = RecipeSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["difficulty", "cooking_time", "author"]
    search_fields = ["title", "description", "ingredients", "tags__name"]
    ordering_fields = ["created_at", "cooking_time", "title"]
    lookup_field = "slug"
    
    def get_serializer_class(self):
        if self.action in ["create", "update", "partial_update"]:
            return RecipeCreateUpdateSerializer
        return RecipeSerializer
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({"request": self.request})
        return context
    
    def get_queryset(self):
        queryset = Recipe.objects.all()
        
        # Show drafts only to their authors
        if self.request.user.is_authenticated:
            queryset = Recipe.objects.filter(status="published") | Recipe.objects.filter(author=self.request.user)
        else:
            queryset = Recipe.objects.filter(status="published")
        
        return queryset
    
    @action(detail=True, methods=["get"])
    def comments(self, request, slug=None):
        recipe = self.get_object()
        comments = Comment.objects.filter(recipe=recipe)
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=["post"])
    def add_comment(self, request, slug=None):
        recipe = self.get_object()
        serializer = CommentSerializer(data=request.data)
        
        if serializer.is_valid():
            serializer.save(author=request.user, recipe=recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=["post"])
    def toggle_like(self, request, slug=None):
        recipe = self.get_object()
        user = request.user
        
        try:
            like = Like.objects.get(recipe=recipe, user=user)
            like.delete()
            return Response({"status": "unliked"}, status=status.HTTP_200_OK)
        except Like.DoesNotExist:
            Like.objects.create(recipe=recipe, user=user)
            return Response({"status": "liked"}, status=status.HTTP_201_CREATED)
    
    @action(detail=False, methods=["get"])
    def my_recipes(self, request):
        if not request.user.is_authenticated:
            return Response(
                {"detail": "Authentication required"}, 
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        recipes = Recipe.objects.filter(author=request.user)
        serializer = RecipeSerializer(
            recipes, many=True, context={"request": request}
        )
        return Response(serializer.data)
    
    @action(detail=False, methods=["get"])
    def my_drafts(self, request):
        if not request.user.is_authenticated:
            return Response(
                {"detail": "Authentication required"}, 
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        recipes = Recipe.objects.filter(author=request.user, status="draft")
        serializer = RecipeSerializer(
            recipes, many=True, context={"request": request}
        )
        return Response(serializer.data)
    
    @action(detail=False, methods=["get"])
    def my_favorites(self, request):
        if not request.user.is_authenticated:
            return Response(
                {"detail": "Authentication required"}, 
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        recipes = request.user.favorite_recipes.all()
        serializer = RecipeSerializer(
            recipes, many=True, context={"request": request}
        )
        return Response(serializer.data) 