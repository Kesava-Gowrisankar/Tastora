from .factories import (
    UserFactory, 
    RecipeFactory, 
    NutritionFactory, 
    IngredientFactory, 
    RecipeImageFactory
)

class RecipeTestDataMixin:

    def _create_entity(self, factory_class, callback=None, **kwargs):

        if callable(callback):
            return callback()
        return factory_class.create(**kwargs)

    def create_test_user(self, callback=None, **kwargs):
        return self._create_entity(UserFactory, callback, **kwargs)

    def create_test_recipe(self, callback=None, **kwargs):
        return self._create_entity(RecipeFactory, callback, **kwargs)

    def create_test_nutrition(self, callback=None, **kwargs):
        return self._create_entity(NutritionFactory, callback, **kwargs)

    def create_test_ingredient(self, callback=None, **kwargs):
        return self._create_entity(IngredientFactory, callback, **kwargs)

    def create_test_image(self, callback=None, **kwargs):
        return self._create_entity(RecipeImageFactory, callback, **kwargs)