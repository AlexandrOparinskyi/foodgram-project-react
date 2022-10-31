from django.contrib import admin
from .models import Ingredients, Tags, Recipe


class IngredientsAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'measurement_unit']


class TagsAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'color', 'slug']


class RecipeAdmin(admin.ModelAdmin):
    list_display = ['id', 'name']


admin.site.register(Ingredients, IngredientsAdmin)
admin.site.register(Tags, TagsAdmin)
admin.site.register(Recipe, RecipeAdmin)
