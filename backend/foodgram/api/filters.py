from django_filters import rest_framework

from recipes.models import Recipes, Tags


class RecipeFilters(rest_framework.FilterSet):
    tags = rest_framework.ModelMultipleChoiceFilter(
        queryset=Tags.objects.all(),
        field_name='tags_slug'
    )
    is_favorite = rest_framework.BooleanFilter(
        method='get_is_favorite'
    )
    is_in_shopping_cart = rest_framework.BooleanFilter(
        method='get_is_in_shopping_cart'
    )

    class Meta:
        model = Recipes
        fields = ['tags', 'is_favorite', 'is_in_shopping_cart', 'author']

    def get_is_favorite(self, queryset, name, value):
        if value:
            return Recipes.objects.filter(
                recipe_favorite__user=self.request.user
            )
        return Recipes.objects.all()

    def get_is_in_shopping_cart(self, queryset, name, value):
        if value:
            return Recipes.objects.filter(
                shopping_recipe__user=self.request.user
            )
        return Recipes.objects.all()
