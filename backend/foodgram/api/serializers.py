from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from djoser.serializers import (UserSerializer,
                                UserCreateSerializer,
                                TokenCreateSerializer)
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from rest_framework.validators import (UniqueValidator,
                                       UniqueTogetherValidator)

from recipes.models import (Ingredients,
                            Tags,
                            Recipes,
                            IngredientsForRecipe,
                            Favorite)


#Users serializers
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
        read_only_fields = ['__all__']

    def get_is_subscribe(self, obj):
        if obj.username in obj.is_subscribe.all():
            return True
        return False


class CustomTokenSerializer(TokenCreateSerializer):
    """
    Сериализатор создания/удаления токена. Метод POST.
    """
    password = serializers.CharField()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = None
        self.fields['email'] = serializers.CharField(required=False)

    def validate(self, attrs):
        password = attrs.get('password')
        params = {'email': attrs.get('email')}
        self.user = authenticate(
            request=self.context.get("request"), **params, password=password
        )
        if not self.user:
            self.user = User.objects.filter(**params).first()
            if self.user and not self.user.check_password(password):
                self.fail("invalid_credentials")
        if self.user and self.user.is_active:
            return attrs
        self.fail("invalid_credentials")


#Recipe serializers
class IngredientsSerializer(serializers.ModelSerializer):
    """
    Сериализатор списка ингредиентов. Метод GET.
    """
    # id = serializers.ReadOnlyField(source='ingredients.id')
    # name = serializers.ReadOnlyField(source='ingredients.name')
    # measurement_unit = serializers.ReadOnlyField(source='ingredients.measurement_unit')

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
    measurement_unit = serializers.ReadOnlyField(source='ingredients.measurement_unit')

    class Meta:
        fields = ['id', 'name', 'measurement_unit', 'amount']
        model = IngredientsForRecipe


class RecipesSerializer(serializers.ModelSerializer):
    """
    Сериализатор создания/просмотра/редактирования/удаления рецептов.
    Методы POST/GET/PATCH/DELETE.
    """
    author = CustomUserSerializer(required=False)
    image = Base64ImageField()
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tags.objects.all(),
        many=True
    )
    ingredients = AddIngredientSerializer(
        many=True,
        write_only=True
    )

    class Meta:
        fields = ['id', 'ingredients', 'tags', 'name',
                  'author', 'image', 'text', 'cooking_time']
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
        instance.tags.set(validated_data.get('tags', instance.tags.all()))
        ingredients = validated_data.pop('ingredients')
        instance.ingredients.clear()
        for ingredient in ingredients:
            IngredientsForRecipe.objects.create(
                recipe=instance,
                ingredients=ingredient['id'],
                amount=ingredient['amount']
            )
        return instance

    def to_representation(self, instance):
        data = super(RecipesSerializer, self).to_representation(instance)
        data['tags'] = TagsSerializer(instance.tags.all(), many=True).data
        data['ingredients'] = ShowIngredientsSerializer(
            instance.recipe_ingredients.all(),
            many=True
        ).data
        return data


#Favorite serializers
class FavoriteSerializer(serializers.ModelSerializer):

    class Meta:
        fields = ['id', 'name', 'image', 'cooking_time']
        model = Recipes
