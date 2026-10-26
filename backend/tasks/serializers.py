from django.utils import timezone
from rest_framework import serializers

from .models import Task


class TaskSerializer(serializers.ModelSerializer):
    assigned_to_name = serializers.CharField(source="assigned_to.username", read_only=True)
    created_by_name = serializers.CharField(source="created_by.username", read_only=True)
    is_overdue = serializers.SerializerMethodField()

    class Meta:
        model = Task
        fields = [
            "id", "title", "description", "status", "due_date",
            "assigned_to", "assigned_to_name", "created_by", "created_by_name",
            "is_overdue", "created_at",
        ]
        read_only_fields = ["created_by", "created_at"]

    def get_is_overdue(self, obj):
        if not obj.due_date or obj.status == "done":
            return False
        return obj.due_date < timezone.now()
