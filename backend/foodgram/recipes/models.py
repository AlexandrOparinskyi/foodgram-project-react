from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator


class Subscribe(models.Model):
    """
    Модель подписок
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscriber',
        verbose_name='Подписчик'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='is_subscribe',
        verbose_name='Автор'
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'],
                name='subscribe',
            )
        ]


class Ingredients(models.Model):
    """
    Модель списка ингредиентов.
    """
    name = models.CharField(
        'Название ингредиента',
        max_length=200
    )
    measurement_unit = models.CharField(
        'Единицы измерения',
        max_length=200
    )

    def __str__(self):
        return self.name


class Tags(models.Model):
    """
    Модель списка тегов.
    """
    name = models.CharField(
        'Название тега',
        max_length=200
    )
    color = models.CharField(
        'Цветовой HEX-код',
        max_length=7
    )
    slug = models.SlugField(
        'Уникальный слаг',
        max_length=200,
        unique=True
    )

    def __str__(self):
        return self.name


class Recipes(models.Model):
    """
    Модель рецептов.
    """
    name = models.CharField(
        'Название рецепта',
        max_length=200
    )
    image = models.ImageField(
        'Картинка',
        upload_to='recipes/images'
    )
    text = models.TextField(
        'Описание'
    )
    cooking_time = models.IntegerField(
        validators=[MinValueValidator(limit_value=1)]
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='author',
        verbose_name='Автор рецепта'
    )
    tags = models.ManyToManyField(
        Tags,
        verbose_name='Тег рецепта'
    )
    ingredients = models.ManyToManyField(
        Ingredients,
        through='IngredientsForRecipe',
        verbose_name='Ингредиент рецепта'
    )

    def __str__(self):
        return self.name


class IngredientsForRecipe(models.Model):
    """
    Модель ингредиентов для создания рецепта.
    """
    recipe = models.ForeignKey(
        Recipes,
        on_delete=models.CASCADE,
        verbose_name='Название рецепта',
        related_name='recipe_ingredients'
    )
    ingredients = models.ForeignKey(
        Ingredients,
        on_delete=models.CASCADE,
        verbose_name='Ингредиент рецепта',
        related_name='ingredients_recipe'
    )
    amount = models.IntegerField(
        'Количество ингредиента',
        validators=[MinValueValidator(1)]
    )


class Favorite(models.Model):
    """
    Модель добавления рецепта в избранное
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='user_favorite'
    )
    recipe = models.ForeignKey(
        Recipes,
        on_delete=models.CASCADE,
        verbose_name='Избранный рецепт',
        related_name='recipe_favorite'
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='favorite'
            )
        ]


class Shopping(models.Model):
    """
    Модель для списка покупок
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='shopping_user',
    )
    recipe = models.ForeignKey(
        Recipes,
        on_delete=models.CASCADE,
        related_name='shopping_recipe'
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='shopping'
            )
        ]
