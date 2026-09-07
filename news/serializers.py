"""
Serializers for the News Application API.

Serializers convert Django model instances into JSON responses and
validate incoming API request data before it is saved to the database.
"""

from rest_framework import serializers

from .models import Article, Publisher, Newsletter, CustomUser


class PublisherSerializer(serializers.ModelSerializer):
    """
    Serializer for Publisher records.

    This exposes all publisher fields through the API when publisher
    data needs to be represented as JSON.
    """

    class Meta:
        model = Publisher
        fields = '__all__'


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for the custom user model.

    Only the user id, username and role are exposed to avoid returning
    sensitive account data such as passwords.
    """

    class Meta:
        model = CustomUser
        fields = [
            'id',
            'username',
            'role'
        ]


class ArticleSerializer(serializers.ModelSerializer):
    """
    Serializer for Article records.

    This serializer is used by the article list, detail, create,
    update and delete API views.
    """

    class Meta:
        model = Article
        fields = '__all__'


class NewsletterSerializer(serializers.ModelSerializer):
    """
    Serializer for Newsletter records.

    This exposes all newsletter fields, including the related articles,
    so newsletters can be represented through the API if required.
    """

    class Meta:
        model = Newsletter
        fields = '__all__'
