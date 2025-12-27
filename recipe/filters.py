import django_filters
from .models import Recipe


class RecipeFilter(django_filters.FilterSet):
    category = django_filters.ChoiceFilter(
        choices=Recipe.CategoryTypes.choices,
        empty_label="All Types"
    )

    difficulty = django_filters.ChoiceFilter(
        choices=Recipe.DifficultyLevels.choices,
        empty_label="All Difficulty"
    )

    cuisine = django_filters.CharFilter(
        field_name="cuisine",
        lookup_expr="icontains"
    )

    search = django_filters.CharFilter(
        field_name="title",
        lookup_expr="icontains",
        label="Search"
    )

    class Meta:
        model = Recipe
        fields = ["category", "difficulty", "cuisine", "search"]
