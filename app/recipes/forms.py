from django import forms
from .models import Recipe, Comment
from django.utils.text import slugify


class RecipeForm(forms.ModelForm):
    class Meta:
        model = Recipe
        fields = [
            "title", "description", "ingredients", "instructions", 
            "cooking_time", "servings", "difficulty", "image", "tags"
        ]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 3}),
            "ingredients": forms.Textarea(attrs={"placeholder": "Enter each ingredient on a new line"}),
            "instructions": forms.Textarea(attrs={"placeholder": "Enter each step on a new line"}),
            "tags": forms.TextInput(attrs={"placeholder": "Enter tags separated by commas"}),
        }
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.slug = slugify(instance.title)
        
        # Check for duplicate slugs and modify if necessary
        from .models import Recipe
        existing_slugs = Recipe.objects.filter(slug__startswith=instance.slug).exclude(id=instance.id)
        if existing_slugs.exists():
            instance.slug = f"{instance.slug}-{existing_slugs.count() + 1}"
        
        if commit:
            instance.save()
            self.save_m2m()
        return instance


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ["text"]
        widgets = {
            "text": forms.Textarea(attrs={"rows": 3, "placeholder": "Share your thoughts on this recipe!"}),
        }


class RecipeSearchForm(forms.Form):
    query = forms.CharField(
        required=False, 
        widget=forms.TextInput(attrs={"placeholder": "Search recipes..."})
    )
    difficulty = forms.ChoiceField(
        choices=[("", "Any Difficulty")] + list(Recipe.DIFFICULTY_CHOICES),
        required=False
    )
    max_cooking_time = forms.IntegerField(
        required=False, 
        min_value=1,
        widget=forms.NumberInput(attrs={"placeholder": "Max cooking time (minutes)"})
    )
    tags = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={"placeholder": "Tags (comma separated)"})
    ) 