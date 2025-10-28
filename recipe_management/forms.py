from django import forms
from recipe.models import Recipe, Nutrition, RecipeImage

class RecipeForm(forms.ModelForm):
    class Meta:
        model = Recipe
        fields = [
            "title", "category", "difficulty", "cuisine",
            "servings", "prep_time", "total_time", "instructions"
        ]

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)  # pass user from view
        super().__init__(*args, **kwargs)

    def clean_title(self):
        title = self.cleaned_data.get('title')
        if self.user and Recipe.objects.filter(title=title, author=self.user).exists():
            raise forms.ValidationError("You already have a recipe with this title.")
        return title

class NutritionForm(forms.ModelForm):
    class Meta:
        model = Nutrition
        fields = ["calories", "protein", "fat", "sugar", "fiber", "carbohydrates"]
        widgets = {
            "calories": forms.NumberInput(attrs={"placeholder": "300 cal"}),
            "protein": forms.NumberInput(attrs={"placeholder": "1 gram"}),
            "fat": forms.NumberInput(attrs={"placeholder": "1 gram"}),
            "sugar": forms.NumberInput(attrs={"placeholder": "1 gram"}),
            "fiber": forms.NumberInput(attrs={"placeholder": "1 gram"}),
            "carbohydrates": forms.NumberInput(attrs={"placeholder": "1 gram"}),
        }

class RecipeImageForm(forms.ModelForm):
    class Meta:
        model = RecipeImage
        fields = ["image"]
