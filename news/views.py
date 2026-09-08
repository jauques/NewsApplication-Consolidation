"""Handle website requests and REST API operations for the News Application.

Website views support registration, article publishing, editor approval,
publisher management, newsletters, and subscription filtering.

REST API views provide authenticated article retrieval and enforce
role-based rules for creating, updating, and deleting articles.
"""

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.core.mail import send_mail
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from .forms import (
    ArticleForm,
    CustomUserRegistrationForm,
    NewsletterForm,
    PublisherForm,
)
from .models import Article, Newsletter, Publisher
from .serializers import ArticleSerializer


def _require_role(user, *roles):
    """Raise PermissionDenied unless the authenticated user has an allowed role."""
    if not user.is_authenticated or user.role not in roles:
        raise PermissionDenied


def _can_manage_article(user, article):
    """Return whether a user may update or delete an article."""
    return user.role == "Editor" or (
        user.role == "Journalist" and article.author_id == user.id
    )


def _can_manage_newsletter(user, newsletter):
    """Return whether a user may update or delete a newsletter."""
    return user.role == "Editor" or (
        user.role == "Journalist" and newsletter.author_id == user.id
    )


def home(request):
    """Display the landing page and latest approved articles."""
    articles = Article.objects.filter(approved=True).select_related(
        "author", "publisher"
    )[:6]
    return render(request, "news/home.html", {"articles": articles})


def register(request):
    """Register a new user and sign the user in."""
    if request.method == "POST":
        form = CustomUserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Registration completed successfully.")
            return redirect("home")
    else:
        form = CustomUserRegistrationForm()
    return render(request, "news/register.html", {"form": form})


def article_list(request):
    """Display all approved articles."""
    articles = Article.objects.filter(approved=True).select_related(
        "author", "publisher"
    )
    return render(request, "news/article_list.html", {"articles": articles})


def article_detail(request, pk):
    """Display one article, subject to approval and ownership rules."""
    article = get_object_or_404(
        Article.objects.select_related("author", "publisher"), pk=pk
    )
    may_preview = request.user.is_authenticated and _can_manage_article(
        request.user, article
    )
    if not article.approved and not may_preview:
        raise PermissionDenied
    return render(request, "news/article_detail.html", {"article": article})


@login_required
def journalist_dashboard(request):
    """Display the logged-in journalist's articles and newsletters."""
    _require_role(request.user, "Journalist")
    articles = Article.objects.filter(author=request.user).select_related(
        "publisher"
    )
    newsletters = Newsletter.objects.filter(author=request.user).prefetch_related(
        "articles"
    )
    return render(
        request,
        "news/journalist_dashboard.html",
        {"articles": articles, "newsletters": newsletters},
    )


@login_required
def editor_dashboard(request):
    """Display article review tools and newsletter information for editors."""
    _require_role(request.user, "Editor")
    pending_articles = Article.objects.filter(approved=False).select_related(
        "author", "publisher"
    )
    approved_articles = Article.objects.filter(approved=True).select_related(
        "author", "publisher"
    )
    newsletters = Newsletter.objects.select_related("author").prefetch_related(
        "articles"
    )
    publishers = Publisher.objects.all()
    return render(
        request,
        "news/editor_dashboard.html",
        {
            "pending_articles": pending_articles,
            "approved_articles": approved_articles,
            "newsletters": newsletters,
            "publishers": publishers,
        },
    )


@login_required
def article_create(request):
    """Allow a journalist to create an article for editor review."""
    _require_role(request.user, "Journalist")
    if request.method == "POST":
        form = ArticleForm(request.POST)
        if form.is_valid():
            article = form.save(commit=False)
            article.author = request.user
            article.approved = False
            article.save()
            messages.success(request, "Article submitted for editor approval.")
            return redirect("journalist-dashboard")
    else:
        form = ArticleForm()
    return render(
        request,
        "news/article_form.html",
        {"form": form, "page_title": "Create Article"},
    )


@login_required
def article_edit(request, pk):
    """Allow an editor or the article's journalist to update an article."""
    article = get_object_or_404(Article, pk=pk)
    if not _can_manage_article(request.user, article):
        raise PermissionDenied
    if request.method == "POST":
        form = ArticleForm(request.POST, instance=article)
        if form.is_valid():
            updated_article = form.save(commit=False)
            if request.user.role == "Journalist":
                updated_article.approved = False
            updated_article.save()
            messages.success(request, "Article updated successfully.")
            destination = (
                "editor-dashboard"
                if request.user.role == "Editor"
                else "journalist-dashboard"
            )
            return redirect(destination)
    else:
        form = ArticleForm(instance=article)
    return render(
        request,
        "news/article_form.html",
        {"form": form, "article": article, "page_title": "Edit Article"},
    )


@login_required
def article_delete(request, pk):
    """Allow an editor or the article's journalist to delete an article."""
    article = get_object_or_404(Article, pk=pk)
    if not _can_manage_article(request.user, article):
        raise PermissionDenied
    if request.method == "POST":
        article.delete()
        messages.success(request, "Article deleted successfully.")
        destination = (
            "editor-dashboard"
            if request.user.role == "Editor"
            else "journalist-dashboard"
        )
        return redirect(destination)
    return render(request, "news/article_confirm_delete.html", {"article": article})


@login_required
def approve_article(request, pk):
    """Allow an editor to approve an article and notify subscribers."""
    _require_role(request.user, "Editor")
    article = get_object_or_404(Article, pk=pk)
    if request.method == "POST":
        article.approved = True
        article.save(update_fields=["approved"])

        recipients = set(
            article.author.journalist_subscribers.exclude(email="").values_list(
                "email", flat=True
            )
        )
        if article.publisher:
            recipients.update(
                article.publisher.subscribers.exclude(email="").values_list(
                    "email", flat=True
                )
            )
        if recipients:
            article_url = request.build_absolute_uri(
                reverse("article-detail", args=[article.pk])
            )
            send_mail(
                subject=f"New approved article: {article.title}",
                message=(
                    f"{article.title}\n\n{article.content}\n\n"
                    f"Read online: {article_url}"
                ),
                from_email=None,
                recipient_list=sorted(recipients),
                fail_silently=True,
            )
        messages.success(request, "Article approved successfully.")
        return redirect("editor-dashboard")
    return render(request, "news/article_approve_confirm.html", {"article": article})


@login_required
def reject_article(request, pk):
    """Allow an editor to reject and remove a submitted article."""
    _require_role(request.user, "Editor")
    article = get_object_or_404(Article, pk=pk, approved=False)
    if request.method == "POST":
        article.delete()
        messages.success(request, "Article rejected and deleted.")
        return redirect("editor-dashboard")
    return render(request, "news/article_reject_confirm.html", {"article": article})


@login_required
def subscribed_articles(request):
    """Display approved articles matching a reader's subscriptions."""
    _require_role(request.user, "Reader")
    articles = Article.objects.filter(approved=True).filter(
        Q(publisher__in=request.user.subscriptions_publishers.all())
        | Q(author__in=request.user.subscriptions_journalists.all())
    ).select_related("author", "publisher").distinct()
    return render(
        request, "news/subscribed_articles.html", {"articles": articles}
    )

def publisher_list(request):
    publishers = Publisher._base_manager.all()
    return render(request, "news/publisher_list.html", {"publishers": publishers})




@login_required
def publisher_create(request):
    """Allow editors to create a publisher through the website."""
    _require_role(request.user, "Editor")
    if request.method == "POST":
        form = PublisherForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Publisher created successfully.")
            return redirect("publisher-list")
    else:
        form = PublisherForm()
    return render(
        request,
        "news/publisher_form.html",
        {"form": form, "page_title": "Create Publisher"},
    )


@login_required
def publisher_edit(request, pk):
    """Allow editors to update a publisher."""
    _require_role(request.user, "Editor")
    publisher = get_object_or_404(Publisher, pk=pk)
    if request.method == "POST":
        form = PublisherForm(request.POST, instance=publisher)
        if form.is_valid():
            form.save()
            messages.success(request, "Publisher updated successfully.")
            return redirect("publisher-list")
    else:
        form = PublisherForm(instance=publisher)
    return render(
        request,
        "news/publisher_form.html",
        {"form": form, "publisher": publisher, "page_title": "Edit Publisher"},
    )


@login_required
def publisher_delete(request, pk):
    """Allow editors to delete a publisher."""
    _require_role(request.user, "Editor")
    publisher = get_object_or_404(Publisher, pk=pk)
    if request.method == "POST":
        publisher.delete()
        messages.success(request, "Publisher deleted successfully.")
        return redirect("publisher-list")
    return render(
        request, "news/publisher_confirm_delete.html", {"publisher": publisher}
    )


def newsletter_list(request):
    """Display newsletters to all users, including readers."""
    newsletters = Newsletter.objects.select_related("author").prefetch_related(
        "articles"
    )
    return render(
        request, "news/newsletter_list.html", {"newsletters": newsletters}
    )


def newsletter_detail(request, pk):
    """Display a newsletter and its approved articles."""
    newsletter = get_object_or_404(
        Newsletter.objects.select_related("author").prefetch_related("articles"),
        pk=pk,
    )
    articles = newsletter.articles.filter(approved=True)
    may_manage = request.user.is_authenticated and _can_manage_newsletter(
        request.user, newsletter
    )
    if may_manage:
        articles = newsletter.articles.all()
    return render(
        request,
        "news/newsletter_detail.html",
        {"newsletter": newsletter, "articles": articles},
    )


@login_required
def newsletter_create(request):
    """Allow journalists and editors to create newsletters."""
    _require_role(request.user, "Journalist", "Editor")
    if request.method == "POST":
        form = NewsletterForm(request.POST, user=request.user)
        if form.is_valid():
            newsletter = form.save(commit=False)
            newsletter.author = request.user
            newsletter.save()
            form.save_m2m()
            messages.success(request, "Newsletter created successfully.")
            return redirect("newsletter-list")
    else:
        form = NewsletterForm(user=request.user)
    return render(
        request,
        "news/newsletter_form.html",
        {"form": form, "page_title": "Create Newsletter"},
    )


@login_required
def newsletter_edit(request, pk):
    """Allow editors or the newsletter's journalist to update it."""
    newsletter = get_object_or_404(Newsletter, pk=pk)
    if not _can_manage_newsletter(request.user, newsletter):
        raise PermissionDenied
    if request.method == "POST":
        form = NewsletterForm(
            request.POST, instance=newsletter, user=request.user
        )
        if form.is_valid():
            form.save()
            messages.success(request, "Newsletter updated successfully.")
            return redirect("newsletter-detail", pk=newsletter.pk)
    else:
        form = NewsletterForm(instance=newsletter, user=request.user)
    return render(
        request,
        "news/newsletter_form.html",
        {
            "form": form,
            "newsletter": newsletter,
            "page_title": "Edit Newsletter",
        },
    )


@login_required
def newsletter_delete(request, pk):
    """Allow editors or the newsletter's journalist to delete it."""
    newsletter = get_object_or_404(Newsletter, pk=pk)
    if not _can_manage_newsletter(request.user, newsletter):
        raise PermissionDenied
    if request.method == "POST":
        newsletter.delete()
        messages.success(request, "Newsletter deleted successfully.")
        return redirect("newsletter-list")
    return render(
        request,
        "news/newsletter_confirm_delete.html",
        {"newsletter": newsletter},
    )


class ArticleListView(generics.ListCreateAPIView):
    """List approved articles and allow journalists to create articles."""

    serializer_class = ArticleSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Article.objects.filter(approved=True).select_related(
            "author", "publisher"
        )

    def perform_create(self, serializer):
        _require_role(self.request.user, "Journalist")
        serializer.save(author=self.request.user, approved=False)


class ArticleDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve approved articles and permit authorised updates or deletion."""

    serializer_class = ArticleSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == "Editor":
            return Article.objects.all()
        if user.role == "Journalist":
            return Article.objects.filter(Q(approved=True) | Q(author=user)).distinct()
        return Article.objects.filter(approved=True)

    def perform_update(self, serializer):
        article = self.get_object()
        if not _can_manage_article(self.request.user, article):
            raise PermissionDenied
        approved = article.approved
        if self.request.user.role == "Journalist":
            approved = False
        serializer.save(author=article.author, approved=approved)

    def perform_destroy(self, instance):
        if not _can_manage_article(self.request.user, instance):
            raise PermissionDenied
        instance.delete()


class SubscribedArticlesView(generics.ListAPIView):
    """Return a reader's approved subscribed articles."""

    serializer_class = ArticleSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        _require_role(self.request.user, "Reader")
        return Article.objects.filter(approved=True).filter(
            Q(publisher__in=self.request.user.subscriptions_publishers.all())
            | Q(author__in=self.request.user.subscriptions_journalists.all())
        ).select_related("author", "publisher").distinct()
