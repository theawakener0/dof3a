from rest_framework.permissions import BasePermission
from ..models import Comment


class IsCommentAuthor(BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user == obj.author
