"""
Database models for the News Application.

This module defines the main data structures used by the project:
CustomUser, Publisher, Article and Newsletter. These models describe
how users, publishers, articles and newsletters are stored in the
MariaDB database through Django's ORM.
"""

from django.db import models
from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):
    """
    Custom user model for the News Application.

    Each user must have a unique email address. Users can share the
    same role, meaning the system can have many Readers, many
    Journalists, and many Editors.
    """

    ROLE_CHOICES = [
        ('Reader', 'Reader'),
        ('Journalist', 'Journalist'),
        ('Editor', 'Editor'),
    ]

    # Ensures that no two users can register with the same email address.
    email = models.EmailField(
        unique=True,
        blank=False
    )

    # Role should NOT be unique because many users can be Readers,
    # Journalists, or Editors.
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES
    )

    subscriptions_publishers = models.ManyToManyField(
        'Publisher',
        blank=True,
        related_name='subscribers'
    )

    subscriptions_journalists = models.ManyToManyField(
        'self',
        blank=True,
        symmetrical=False,
        related_name='journalist_subscribers'
    )

    def __str__(self):
        return self.username


class Publisher(models.Model):
    """
    Represents a news publisher.

    A publisher can have many articles linked to it. Readers can also
    subscribe to publishers so that they can retrieve articles from
    selected publishers using the subscribed articles API endpoint.
    """

    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    def __str__(self):
        """Return the publisher's name for readable display.

        Returns:
            str: The publisher name displayed in Django admin
            and other text representations.
        """
        return self.name


class Article(models.Model):
    """
    Represents a news article created by a journalist.

    Each article has an author, optional publisher, creation date,
    and approval status. The approved field controls whether the
    article is visible through the public article API responses.
    """

    title = models.CharField(max_length=200)
    content = models.TextField()

    # Links each article to the user who created it.
    author = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='articles'
    )

    # Links the article to a publisher. SET_NULL keeps the article
    # available even if the publisher record is removed.
    publisher = models.ForeignKey(
        Publisher,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    # Editors can use this field to mark articles as approved.
    approved = models.BooleanField(default=False)

    def __str__(self):
        """
        Return the article title for readable display.
        """
        return self.title


class Newsletter(models.Model):
    """
    Represents a newsletter created by a journalist.

    A newsletter can contain multiple articles through a ManyToMany
    relationship. This allows one newsletter to group several articles
    together for readers.
    """

    title = models.CharField(max_length=200)

    description = models.TextField()

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    # Links each newsletter to the user who created it.
    author = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='newsletters'
    )

    # Allows a newsletter to contain multiple articles.
    articles = models.ManyToManyField(
        Article,
        blank=True
    )

    def __str__(self):
        """
        Return the newsletter title for readable display.
        """
        return self.title
