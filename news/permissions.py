"""
Custom permission classes for the News Application.

These permissions are used by the API views to enforce role-based
access control for journalists and editors.
"""

from rest_framework.permissions import BasePermission


class IsEditor(BasePermission):
    """
    Allow access only to authenticated users with the Editor role.

    Editors are responsible for approving and deleting article content.
    """

    def has_permission(self, request, view):
        """
        Check whether the current user is authenticated and is an editor.
        """
        return (
            request.user.is_authenticated and
            request.user.role == "Editor"
        )


class IsJournalist(BasePermission):
    """
    Allow access only to authenticated users with the Journalist role.

    Journalists are responsible for creating and updating article content.
    """

    def has_permission(self, request, view):
        """
        Check whether the current user is authenticated and is a journalist.
        """
        return (
            request.user.is_authenticated and
            request.user.role == "Journalist"
        )
