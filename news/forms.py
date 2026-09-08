"""
Forms for the News Application website.

This module contains forms for user registration, articles,
publishers, and newsletters.
"""

from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import Article, CustomUser, Newsletter, Publisher


class CustomUserRegistrationForm(UserCreationForm):
    """
    Register a new user with a username, unique email address, and role.
    """

    email = forms.EmailField(required=True)

    class Meta:
        model = CustomUser
        fields = (
            "username",
            "email",
            "role",
            "password1",
            "password2",
        )

    def clean_email(self):
        """Validate and normalise the registration email address.

        Returns:
            str: The email address with surrounding whitespace removed
            and all letters converted to lowercase.

        Raises:
            forms.ValidationError: If another user already has this
                email address, ignoring letter case.
        
        """

        email = self.cleaned_data["email"].strip().lower()

        if CustomUser.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError(
                "A user with this email address already exists."
            )

        return email


class ArticleForm(forms.ModelForm):
    """
    Create or edit an article.

    The author and approval status are controlled by the application
    and are therefore not available as editable form fields.
    """

    class Meta:
        model = Article
        fields = (
            "title",
            "content",
            "publisher",
        )
        widgets = {
            "title": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter the article title",
                }
            ),
            "content": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 10,
                    "placeholder": "Enter the article content",
                }
            ),
            "publisher": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),
        }


class PublisherForm(forms.ModelForm):
    """
    Create or edit a publisher through the website.

    Publisher management is restricted to users with the Editor role
    through the corresponding views.
    """

    class Meta:
        model = Publisher
        fields = (
            "name",
            "description",
        )
        widgets = {
            "name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter the publisher name",
                }
            ),
            "description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 5,
                    "placeholder": "Enter the publisher description",
                }
            ),
        }


class NewsletterForm(forms.ModelForm):
    """
    Create or edit a newsletter.

    Journalists may select their own articles. Editors may select
    articles belonging to any journalist.
    """

    class Meta:
        model = Newsletter
        fields = (
            "title",
            "description",
            "articles",
        )
        widgets = {
            "title": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter the newsletter title",
                }
            ),
            "description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 6,
                    "placeholder": "Enter the newsletter description",
                }
            ),
            "articles": forms.CheckboxSelectMultiple(),
        }

    def __init__(self, *args, user=None, **kwargs):
        """
        Limit the article choices according to the current user's role.
        """

        super().__init__(*args, **kwargs)

        articles = Article.objects.all()

        if user and user.role == "Journalist":
            articles = articles.filter(author=user)

        self.fields["articles"].queryset = articles