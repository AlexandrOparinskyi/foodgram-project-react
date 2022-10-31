from django.db import models
from django.contrib.auth.models import User


class Subscribe(models.Model):
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


class Amount(models.Model):
    amount = models.IntegerField(
        'Количество ингредиентов',
        default=1
    )


class Ingredients(models.Model):
    name = models.CharField(
        'Название ингредиента',
        max_length=200
    )
    measurement_unit = models.CharField(
        'Единицы измерения',
        max_length=200
    )
    amount = models.ForeignKey(
        Amount,
        on_delete=models.SET_DEFAULT,
        default=1,
        related_name='count',
        verbose_name='Количество ингредиентов',
        null=True
    )

    def __str__(self):
        return self.name


class Tags(models.Model):
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


class Recipe(models.Model):
    name = models.CharField(
        'Название рецепта',
        max_length=200
    )
    image = models.TextField(
        'Картинка'
    )
    text = models.TextField(
        'Описание рецепта'
    )
    cooking_time = models.IntegerField(
        'Время приготовления (в минутах)',
        default=1,
    )
    ingredients = models.ManyToManyField(
        Ingredients,
        related_name='ingredients'
    )
    tags = models.ManyToManyField(
        Tags,
        related_name='tags'
    )

    def __str__(self):
        return self.name
