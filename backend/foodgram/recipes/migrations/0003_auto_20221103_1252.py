# Generated by Django 3.2 on 2022-11-03 09:52

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0002_alter_ingredientsforrecipe_recipe'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ingredientsforrecipe',
            name='ingredients',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ingredients_recipe', to='recipes.ingredients', verbose_name='Ингредиент рецепта'),
        ),
        migrations.AlterField(
            model_name='ingredientsforrecipe',
            name='recipe',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='recipe_ingredients', to='recipes.recipes', verbose_name='Название рецепта'),
        ),
    ]
