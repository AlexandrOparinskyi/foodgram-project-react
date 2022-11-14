from django_filters import rest_framework
from django_filters import filters

from recipes.models import Recipes, Tags, Ingredients


class RecipeFilters(rest_framework.FilterSet):
    tags = rest_framework.ModelMultipleChoiceFilter(
        queryset=Tags.objects.all(),
        field_name='tags__slug',
        to_field_name='slug'
    )
    is_favorite = filters.NumberFilter(
        method='get_is_favorite'
    )
    is_in_shopping_cart = filters.NumberFilter(
        method='get_is_in_shopping_cart'
    )

    class Meta:
        model = Recipes
        fields = ['tags', 'is_favorite', 'is_in_shopping_cart', 'author']

    def get_is_favorite(self, queryset, name, value):
        if value:
            return queryset.filter(
                recipe_favorite__user=self.request.user
            )
        return Recipes.objects.all()

    def get_is_in_shopping_cart(self, queryset, name, value):
        if value:
            return queryset.filter(
                shopping_recipe__user=self.request.user
            )
        return Recipes.objects.all()


class IngredientsFilter(rest_framework.FilterSet):
    name = filters.CharFilter(
        field_name='name',
        lookup_expr='istartswith',
    )

    class Meta:
        model = Ingredients
        fields = ['name', 'measurement_unit']
