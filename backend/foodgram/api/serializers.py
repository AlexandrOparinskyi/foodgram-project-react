import base64

from django.contrib.auth.models import User
from django.core.files.base import ContentFile
from djoser.serializers import (UserSerializer,
                                UserCreateSerializer)
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from django.core.validators import MaxValueValidator

from recipes.models import (Ingredients,
                            Tags,
                            Recipes,
                            IngredientsForRecipe,
                            Subscribe,
                            Favorite,
                            Shopping)


class CustomUserCreateSerializer(UserCreateSerializer):
    """
    Сериализатор для регистрации пользователя. Метод POST.
    """
    email = serializers.EmailField(
        validators=[UniqueValidator(User.objects.all())]
    )

    class Meta:
        fields = ['id', 'email', 'username', 'first_name',
                  'last_name', 'password']
        model = User
        extra_kwargs = {
            'password': {
                'write_only': True,
                'max_length': 150
            },
            'email': {
                'required': True,
                'max_length': 254,
            },
            'username': {
                'max_length': 150
            },
            'first_name': {
                'required': True,
                'max_length': 150
            },
            'last_name': {
                'required': True,
                'max_length': 150
            },
        }

    def create(self, validated_data):
        user = User(
            email=validated_data['email'],
            username=validated_data['username'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name']
        )
        user.set_password(validated_data['password'])
        user.save()
        return user


class CustomUserSerializer(UserSerializer):
    """
    Сериализатор пользователя. Метод GET.
    """
    is_subscribe = serializers.SerializerMethodField(
        required=False
    )

    class Meta:
        fields = ['id', 'email', 'username', 'first_name',
                  'last_name', 'is_subscribe']
        model = User

    def get_is_subscribe(self, obj):
        return Subscribe.objects.filter(
            user_id=self.context.get('request').user.id,
            author_id=obj.id
        ).exists()


class IngredientsSerializer(serializers.ModelSerializer):
    """
    Сериализатор списка ингредиентов. Метод GET.
    """

    class Meta:
        fields = ['id', 'name', 'measurement_unit']
        model = Ingredients


class TagsSerializer(serializers.ModelSerializer):
    """
    Сериализатор списка тегов. Метод GET.
    """

    class Meta:
        fields = ['id', 'name', 'color', 'slug']
        model = Tags


class AddIngredientSerializer(serializers.ModelSerializer):
    """
    Сериализатор добавления ингредиентов к рецепту.
    """
    amount = serializers.IntegerField()
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredients.objects.all()
    )

    class Meta:
        fields = ['id', 'amount']
        model = IngredientsForRecipe


class ShowIngredientsSerializer(serializers.ModelSerializer):
    """
    Сериализатор показа ингредиентов после добавления в рецепт.
    """
    id = serializers.ReadOnlyField(source='ingredients.id')
    name = serializers.ReadOnlyField(source='ingredients.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredients.measurement_unit'
    )

    class Meta:
        fields = ['id', 'name', 'measurement_unit', 'amount']
        model = IngredientsForRecipe


class CustomBase64Image(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='image.' + ext)
        return super().to_internal_value(data)


class RecipesSerializer(serializers.ModelSerializer):
    """
    Сериализатор создания/просмотра/редактирования/удаления рецептов.
    Методы POST/GET/PATCH/DELETE.
    """
    author = CustomUserSerializer(required=False)
    image = CustomBase64Image()
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tags.objects.all(),
        many=True
    )
    ingredients = AddIngredientSerializer(
        many=True,
        write_only=True
    )
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        fields = ['id', 'ingredients', 'tags', 'name',
                  'author', 'image', 'text', 'cooking_time',
                  'is_favorited', 'is_in_shopping_cart']
        model = Recipes

    def create(self, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe = Recipes.objects.create(**validated_data)
        for tag in tags:
            recipe.tags.add(tag)
        for ingredient in ingredients:
            created = IngredientsForRecipe.objects.create(
                recipe=recipe,
                amount=ingredient['amount'],
                ingredients=ingredient['id'],
            )
            created.save()
        return recipe

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.image = validated_data.get('image', instance.image)
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = validated_data.get(
            'cooking_time',
            instance.cooking_time
        )
        instance.tags.set(validated_data.get('tags', instance.tags.all()))
        ingredients = validated_data.pop('ingredients')
        instance.ingredients.clear()
        for ingredient in ingredients:
            IngredientsForRecipe.objects.create(
                recipe=instance,
                ingredients=ingredient['id'],
                amount=ingredient['amount']
            )
        instance.save()
        return instance

    def to_representation(self, instance):
        data = super(RecipesSerializer, self).to_representation(instance)
        data['tags'] = TagsSerializer(instance.tags.all(), many=True).data
        data['ingredients'] = ShowIngredientsSerializer(
            instance.recipe_ingredients.all(),
            many=True
        ).data
        return data

    def get_is_favorited(self, obj):
        return Favorite.objects.filter(
            user=self.context.get('request').user,
            recipe=obj
        ).exists()

    def get_is_in_shopping_cart(self, obj):
        return Shopping.objects.filter(
            user=self.context.get('request').user,
            recipe=obj
        ).exists()


class FavoriteSerializer(serializers.ModelSerializer):

    class Meta:
        fields = ['id', 'name', 'image', 'cooking_time']
        model = Recipes


class SubscribeSerializer(serializers.ModelSerializer):
    recipes = serializers.SerializerMethodField()
    is_subscribe = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        fields = ['email', 'id', 'username', 'first_name',
                  'last_name', 'is_subscribe', 'recipes', 'recipes_count']
        model = User

    def get_recipes(self, obj):
        recipes = Recipes.objects.filter(author=obj)
        return FavoriteSerializer(
            recipes,
            many=True,
            validators=[MaxValueValidator(3)],
            context={'request': self.context.get('request')}
        ).data

    def get_is_subscribe(self, obj):
        return Subscribe.objects.filter(
            user_id=self.context.get('request').user.id,
            author_id=obj.id
        ).exists()

    def get_recipes_count(self, obj):
        return Recipes.objects.filter(author=obj).count()
