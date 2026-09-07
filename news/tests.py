"""
Automated API tests for the News Application.

These tests verify that the main article API endpoints work correctly
and that authentication and role-based permissions are enforced.
"""

from rest_framework import status
from rest_framework.test import APITestCase

from .models import Article, CustomUser, Publisher


class ArticleAPITestCase(APITestCase):
    """
    Test suite for article API functionality.

    The tests create sample users, a publisher, and an article. They
    verify authenticated access, unauthenticated access, article detail
    retrieval, journalist article creation, and reader restrictions.
    """

    def setUp(self):
        """
        Create test data used by each test case.

        A reader, journalist, editor, publisher, and approved article
        are created in the temporary test database.
        """

        self.reader = CustomUser.objects.create_user(
            username="reader_test",
            email="reader_test@test.com",
            password="Password123!",
            role="Reader",
        )

        self.journalist = CustomUser.objects.create_user(
            username="journalist_test",
            email="journalist_test@test.com",
            password="Password123!",
            role="Journalist",
        )

        self.editor = CustomUser.objects.create_user(
            username="editor_test",
            email="editor_test@test.com",
            password="Password123!",
            role="Editor",
        )

        self.publisher = Publisher.objects.create(
            name="Tech Daily",
        )

        self.article = Article.objects.create(
            title="Test Article",
            content="Test Content",
            author=self.journalist,
            publisher=self.publisher,
            approved=True,
        )

    def test_articles_list_authenticated(self):
        """
        Verify that an authenticated user can retrieve the article list.
        """

        self.client.force_authenticate(user=self.reader)

        response = self.client.get("/api/articles/")

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

    def test_articles_list_unauthenticated(self):
        """
        Verify that anonymous users cannot retrieve the article list.
        """

        response = self.client.get("/api/articles/")

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    def test_article_detail(self):
        """
        Verify that an authenticated user can retrieve one article.
        """

        self.client.force_authenticate(user=self.reader)

        response = self.client.get(
            f"/api/articles/{self.article.id}/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

    def test_journalist_can_create_article(self):
        """
        Verify that a journalist can create an article through the API.
        """

        self.client.force_authenticate(user=self.journalist)

        data = {
            "title": "New API Article",
            "content": "Testing article creation",
            "author": self.journalist.id,
            "publisher": self.publisher.id,
            "approved": False,
        }

        response = self.client.post(
            "/api/articles/",
            data,
            format="json",
        )

        self.assertIn(
            response.status_code,
            [
                status.HTTP_200_OK,
                status.HTTP_201_CREATED,
            ],
        )

    def test_reader_cannot_create_article(self):
        """
        Verify that a reader cannot create an article through the API.
        """

        self.client.force_authenticate(user=self.reader)

        data = {
            "title": "Blocked Article",
            "content": "Should fail",
            "author": self.reader.id,
            "publisher": self.publisher.id,
            "approved": False,
        }

        response = self.client.post(
            "/api/articles/",
            data,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )