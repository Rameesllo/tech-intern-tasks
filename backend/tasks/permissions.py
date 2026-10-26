from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsAssigneeOrCreatorOrReadOnly(BasePermission):
    """Anyone authenticated can read; only creator can delete; assignee or creator can edit."""

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        if request.method == "DELETE":
            return obj.created_by == request.user
        return request.user in (obj.assigned_to, obj.created_by)
