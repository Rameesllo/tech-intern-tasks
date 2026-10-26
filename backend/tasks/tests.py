import datetime
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.test import APITestCase

from .models import Task


class TaskApiTests(APITestCase):
    def setUp(self):
        User = get_user_model()
        self.alice = User.objects.create_user("alice", password="password123")
        self.bob = User.objects.create_user("bob", password="password123")
        self.carol = User.objects.create_user("carol", password="password123")
        self.task = Task.objects.create(
            title="Sample",
            assigned_to=self.alice,
            created_by=self.alice,
            due_date=timezone.now(),
        )

    def test_list_requires_auth(self):
        response = self.client.get("/api/tasks/")
        self.assertEqual(response.status_code, 401)

    def test_list_tasks_all_authenticated_users(self):
        self.client.force_authenticate(self.carol)
        response = self.client.get("/api/tasks/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 1)

    def test_filter_by_status(self):
        Task.objects.create(
            title="Done task",
            assigned_to=self.alice,
            created_by=self.alice,
            status="done",
        )
        self.client.force_authenticate(self.alice)
        response = self.client.get("/api/tasks/?status=done")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["status"], "done")

    def test_sorting_due_date_nulls_last(self):
        Task.objects.all().delete()
        now = timezone.now()
        t_no_due = Task.objects.create(
            title="No Due", assigned_to=self.alice, created_by=self.alice, due_date=None
        )
        t_future = Task.objects.create(
            title="Future",
            assigned_to=self.alice,
            created_by=self.alice,
            due_date=now + datetime.timedelta(days=2),
        )
        t_past = Task.objects.create(
            title="Past",
            assigned_to=self.alice,
            created_by=self.alice,
            due_date=now - datetime.timedelta(days=2),
        )
        self.client.force_authenticate(self.alice)
        response = self.client.get("/api/tasks/")
        ids = [item["id"] for item in response.data["results"]]
        self.assertEqual(ids, [t_past.id, t_future.id, t_no_due.id])

    def test_edit_permission_assignee_and_creator(self):
        # Alice is creator and assignee
        self.client.force_authenticate(self.alice)
        res = self.client.patch(f"/api/tasks/{self.task.id}/", {"title": "Updated by Alice"})
        self.assertEqual(res.status_code, 200)

        # Assign task to bob (created by alice)
        self.task.assigned_to = self.bob
        self.task.save()

        # Bob (assignee) can edit
        self.client.force_authenticate(self.bob)
        res = self.client.patch(f"/api/tasks/{self.task.id}/", {"title": "Updated by Bob"})
        self.assertEqual(res.status_code, 200)

        # Alice (creator) can edit
        self.client.force_authenticate(self.alice)
        res = self.client.patch(f"/api/tasks/{self.task.id}/", {"title": "Updated by Alice Again"})
        self.assertEqual(res.status_code, 200)

        # Carol (neither) cannot edit
        self.client.force_authenticate(self.carol)
        res = self.client.patch(f"/api/tasks/{self.task.id}/", {"title": "Updated by Carol"})
        self.assertEqual(res.status_code, 403)

    def test_delete_permission_creator_only(self):
        self.task.assigned_to = self.bob
        self.task.created_by = self.alice
        self.task.save()

        # Bob (assignee, not creator) cannot delete
        self.client.force_authenticate(self.bob)
        res = self.client.delete(f"/api/tasks/{self.task.id}/")
        self.assertEqual(res.status_code, 403)

        # Carol (neither) cannot delete
        self.client.force_authenticate(self.carol)
        res = self.client.delete(f"/api/tasks/{self.task.id}/")
        self.assertEqual(res.status_code, 403)

        # Alice (creator) can delete
        self.client.force_authenticate(self.alice)
        res = self.client.delete(f"/api/tasks/{self.task.id}/")
        self.assertEqual(res.status_code, 204)

    def test_creator_assigned_from_auth_user_not_client_input(self):
        self.client.force_authenticate(self.alice)
        res = self.client.post(
            "/api/tasks/",
            {
                "title": "New Task",
                "assigned_to": self.bob.id,
                "created_by": self.carol.id,
            },
        )
        self.assertEqual(res.status_code, 201)
        self.assertEqual(res.data["created_by"], self.alice.id)

    def test_is_overdue_badge_calculation(self):
        now = timezone.now()
        past_task = Task.objects.create(
            title="Past Todo",
            assigned_to=self.alice,
            created_by=self.alice,
            due_date=now - datetime.timedelta(hours=2),
            status="todo",
        )
        done_past_task = Task.objects.create(
            title="Past Done",
            assigned_to=self.alice,
            created_by=self.alice,
            due_date=now - datetime.timedelta(hours=2),
            status="done",
        )
        self.client.force_authenticate(self.alice)
        res1 = self.client.get(f"/api/tasks/{past_task.id}/")
        self.assertTrue(res1.data["is_overdue"])

        res2 = self.client.get(f"/api/tasks/{done_past_task.id}/")
        self.assertFalse(res2.data["is_overdue"])

    def test_query_count_efficiency(self):
        # Create multiple tasks with assigned and creator users
        for i in range(10):
            Task.objects.create(
                title=f"Task {i}",
                assigned_to=self.bob,
                created_by=self.alice,
            )
        self.client.force_authenticate(self.alice)
        # 1 count query + 1 tasks query with joined users
        with self.assertNumQueries(2):
            res = self.client.get("/api/tasks/")
            self.assertEqual(res.status_code, 200)

    def test_task_stats_for_logged_in_user(self):
        Task.objects.all().delete()
        now = timezone.now()

        # Alice's tasks:
        # 1 todo (not overdue)
        Task.objects.create(
            title="Alice Todo Future",
            assigned_to=self.alice,
            created_by=self.alice,
            status="todo",
            due_date=now + datetime.timedelta(days=1),
        )
        # 1 in_progress (overdue)
        Task.objects.create(
            title="Alice In Progress Overdue",
            assigned_to=self.alice,
            created_by=self.alice,
            status="in_progress",
            due_date=now - datetime.timedelta(hours=2),
        )
        # 1 done (past due date, but completed so NOT counted in overdue)
        Task.objects.create(
            title="Alice Done Past",
            assigned_to=self.alice,
            created_by=self.alice,
            status="done",
            due_date=now - datetime.timedelta(hours=5),
        )
        # Bob's task (should not count in Alice's stats)
        Task.objects.create(
            title="Bob Todo",
            assigned_to=self.bob,
            created_by=self.alice,
            status="todo",
            due_date=now - datetime.timedelta(days=1),
        )

        self.client.force_authenticate(self.alice)
        # Exactly 1 single aggregate SQL query
        with self.assertNumQueries(1):
            response = self.client.get("/api/tasks/stats/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.data,
            {
                "todo": 1,
                "in_progress": 1,
                "done": 1,
                "overdue": 1,
            },
        )
