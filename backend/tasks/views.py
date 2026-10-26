from django.db.models import Count, F, Q
from django.utils import timezone
from rest_framework import permissions, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Task
from .permissions import IsAssigneeOrCreatorOrReadOnly
from .serializers import TaskSerializer


class TaskViewSet(viewsets.ModelViewSet):
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated, IsAssigneeOrCreatorOrReadOnly]

    def get_queryset(self):
        queryset = (
            Task.objects.all()
            .select_related("assigned_to", "created_by")
            .order_by(F("due_date").asc(nulls_last=True))
        )
        status_param = self.request.query_params.get("status")
        if status_param:
            queryset = queryset.filter(status=status_param)
        return queryset

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(detail=False, methods=["get"])
    def stats(self, request):
        now = timezone.now()
        stats = Task.objects.filter(assigned_to=request.user).aggregate(
            todo=Count("id", filter=Q(status="todo")),
            in_progress=Count("id", filter=Q(status="in_progress")),
            done=Count("id", filter=Q(status="done")),
            overdue=Count("id", filter=Q(due_date__lt=now) & ~Q(status="done")),
        )
        return Response(stats)
