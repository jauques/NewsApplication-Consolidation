"""URL routes for the News Application."""

from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("register/", views.register, name="register"),

    path("articles/", views.article_list, name="article-list"),
    path("articles/create/", views.article_create, name="article-create"),
    path("articles/subscribed/", views.subscribed_articles, name="subscribed-articles"),
    path("articles/<int:pk>/", views.article_detail, name="article-detail"),
    path("articles/<int:pk>/edit/", views.article_edit, name="article-edit"),
    path("articles/<int:pk>/delete/", views.article_delete, name="article-delete"),

    path("dashboard/", views.journalist_dashboard, name="journalist-dashboard"),
    path("editor/", views.editor_dashboard, name="editor-dashboard"),
    path(
        "editor/articles/<int:pk>/approve/",
        views.approve_article,
        name="approve-article",
    ),
    path(
        "editor/articles/<int:pk>/reject/",
        views.reject_article,
        name="reject-article",
    ),

    path("publishers/", views.publisher_list, name="publisher-list"),
    path("publishers/create/", views.publisher_create, name="publisher-create"),
    path("publishers/<int:pk>/edit/", views.publisher_edit, name="publisher-edit"),
    path(
        "publishers/<int:pk>/delete/",
        views.publisher_delete,
        name="publisher-delete",
    ),

    path("newsletters/", views.newsletter_list, name="newsletter-list"),
    path("newsletters/create/", views.newsletter_create, name="newsletter-create"),
    path("newsletters/<int:pk>/", views.newsletter_detail, name="newsletter-detail"),
    path(
        "newsletters/<int:pk>/edit/",
        views.newsletter_edit,
        name="newsletter-edit",
    ),
    path(
        "newsletters/<int:pk>/delete/",
        views.newsletter_delete,
        name="newsletter-delete",
    ),

    path("api/articles/", views.ArticleListView.as_view(), name="api-article-list"),
    path(
        "api/articles/subscribed/",
        views.SubscribedArticlesView.as_view(),
        name="api-subscribed-articles",
    ),
    path(
        "api/articles/<int:pk>/",
        views.ArticleDetailView.as_view(),
        name="api-article-detail",
    ),
]
