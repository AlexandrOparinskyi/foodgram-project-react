from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator


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
        verbose_name='Количество',
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


class Recipes(models.Model):
    name = models.CharField(
        'Название рецепта',
        max_length=200
    )
    image = models.ImageField(
        'Картинка',
        upload_to='media'
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
