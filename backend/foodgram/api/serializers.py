from rest_framework import serializers
from django.contrib.auth.models import User


class CustomUserCreateSerializer(serializers.ModelSerializer):

    class Meta:
        fields = ['id', 'email', 'username', 'first_name',
                  'last_name', 'password']
        model = User
        extra_kwargs = {
            'password': {'write_only': True},
            'email': {'required': True},
            'first_name': {'required': True},
            'last_name': {'required': True},
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


class CustomUserSerializer(serializers.ModelSerializer):

    class Meta:
        fields = ['id', 'email', 'username',
                  'first_name', 'last_name']
        model = User
