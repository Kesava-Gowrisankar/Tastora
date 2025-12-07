from decimal import Decimal
from django import forms
from recipe.models import Ingredient, Recipe, Nutrition, RecipeImage

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

class IngredientForm(forms.ModelForm):

    class Meta:
        model = Ingredient
        fields = ["name", "quantity", "unit", "optional"]
        widgets = {
            "name": forms.TextInput(attrs={"placeholder": "e.g., Sugar"}),
            "quantity": forms.NumberInput(attrs={"placeholder": "e.g., 100"}),
            "unit": forms.Select(choices=Ingredient.UnitTypes.choices),
            "optional": forms.CheckboxInput(),
        }
IngredientFormSetClass = forms.modelformset_factory(Ingredient, form=IngredientForm, extra=1, can_delete=False)
