import random
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.utils import timezone

from tasks.models import Task

TITLES = [
    "Fix login redirect", "Write API docs", "Design onboarding screen", "Set up CI",
    "Refactor payment module", "Add dark mode", "Review PR #42", "Update dependencies",
    "Investigate slow dashboard", "Add push notifications", "Write unit tests",
    "Migrate to new S3 bucket", "Clean up feature flags", "Prepare sprint demo",
    "Fix crash on Android 12",
]


class Command(BaseCommand):
    help = "Seed users (alice, bob, carol / password123) and 30 tasks"

    def handle(self, *args, **options):
        random.seed(42)
        User = get_user_model()
        users = []
        for name in ["alice", "bob", "carol"]:
            user, _ = User.objects.get_or_create(username=name)
            user.set_password("password123")
            user.save()
            users.append(user)

        Task.objects.all().delete()
        now = timezone.now()
        for i in range(30):
            Task.objects.create(
                title=f"{random.choice(TITLES)} ({i + 1})",
                status=random.choice(["todo", "in_progress", "done"]),
                due_date=None if i % 8 == 0 else now + timedelta(days=random.randint(-10, 10), hours=random.randint(0, 23)),
                assigned_to=random.choice(users),
                created_by=random.choice(users),
            )
        self.stdout.write(self.style.SUCCESS("Seeded 3 users and 30 tasks."))
