from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from djoser.serializers import (UserSerializer,
                                UserCreateSerializer,
                                TokenCreateSerializer)
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from drf_extra_fields.fields import Base64ImageField

from recipes.models import (Ingredients,
                            Tags,
                            Recipes)


class CustomUserCreateSerializer(UserCreateSerializer):
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
    is_subscribe = serializers.SerializerMethodField(
        required=False
    )

    class Meta:
        fields = ['id', 'email', 'username', 'first_name',
                  'last_name', 'is_subscribe']
        model = User
        read_only_fields = ['__all__']

    def get_is_subscribe(self, obj):
        return False


class CustomTokenSerializer(TokenCreateSerializer):
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


class IngredientsSerializer(serializers.ModelSerializer):
    amount = serializers.IntegerField()

    class Meta:
        fields = ['id', 'name', 'measurement_unit', 'amount']
        model = Ingredients


class TagsSerializer(serializers.ModelSerializer):

    class Meta:
        fields = ['id', 'name', 'color', 'slug']
        model = Tags


class RecipesSerializer(serializers.ModelSerializer):
    author = CustomUserSerializer(required=False)
    image = Base64ImageField()

    class Meta:
        fields = ['id', 'name', 'author', 'image', 'text', 'cooking_time']
        model = Recipes
