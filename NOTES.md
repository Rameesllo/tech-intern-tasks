# Notes

## Task Status Report

| Task | File/Area | Symptoms | Root Cause | How You Fixed It | Fixed? |
|---|---|---|---|---|---|
| 1. Status Filter | `backend/tasks/views.py`, `frontend/src/App.jsx` | Changing status dropdown does not filter tasks. | Backend filtered on parameter `state` instead of `status`; frontend `useEffect` dependency array omitted `status`. | Changed query parameter to `status` in `views.py`; added `status` to `useEffect` dependency array in `App.jsx`. | Yes |
| 2. Mark Done UI Update | `frontend/src/App.jsx` | Clicking "Mark done" does not immediately update button or badge in the UI. | Direct state mutation on the task object and passing the identical array reference to `setTasks(tasks)`, causing React to skip re-rendering. | Replaced mutation with an immutable state update using `setTasks(prev => prev.map(...))` to return new object and array references. | Yes |
| 3. Edit Permissions | `backend/tasks/permissions.py` | Non-assignees and non-creators can edit tasks. | Faulty boolean condition `obj.assigned_to or obj.created_by == request.user` evaluated truthiness of `obj.assigned_to` instead of equality with `request.user`. | Changed condition to `request.user in (obj.assigned_to, obj.created_by)` for write requests. | Yes |
| 4. Delete Permissions | `backend/tasks/permissions.py` | Assignees can delete tasks they did not create. | Permission class treated all mutation methods (PUT, PATCH, DELETE) identically without isolating DELETE operations. | Added explicit check: `if request.method == "DELETE": return obj.created_by == request.user`. | Yes |
| 5. Authenticated Task Viewing | `backend/tasks/permissions.py`, `backend/tasks/views.py` | All authenticated users must be able to view tasks. | Need to verify that SAFE_METHODS are universally permitted for authenticated users. | Confirmed `request.method in SAFE_METHODS` returns `True` and `IsAuthenticated` is enforced on viewset. | Yes |
| 6. Task Creator Security | `backend/tasks/views.py`, `backend/tasks/serializers.py` | Malicious clients can spoof task creator by passing `created_by` in POST body. | `perform_create` trusted client data (`serializer.validated_data.get("created_by") or self.request.user`), and `created_by` was not marked read-only. | Added `created_by` to `read_only_fields` in `TaskSerializer`; enforced `serializer.save(created_by=self.request.user)` in `perform_create`. | Yes |
| 7. Due Date Sorting | `backend/tasks/views.py` | Tasks with no due date appeared at top of list instead of at the end. | Default SQL `ORDER BY due_date` places `NULL` values first in SQLite. | Replaced `.order_by("due_date")` with `.order_by(F("due_date").asc(nulls_last=True))`. | Yes |
| 8. Total Task Count | `frontend/src/App.jsx` | Task counter displays only 20 tasks instead of total seeded count (30 tasks). | UI rendered `tasks.length` (the current page slice size) rather than total count from DRF's paginated response. | Stored `data.count` from the DRF response in `totalCount` state and displayed `{totalCount} tasks`. | Yes |
| 9. Overdue Calculation | `backend/tasks/serializers.py` | Overdue badge failed for same-day past times and used deprecated UTC method. | Serializer compared date-only values with deprecated, timezone-naive `datetime.utcnow().date()`. | Updated comparison to `obj.due_date < timezone.now()` using Django's timezone-aware datetime. | Yes |
| 10. List Query Efficiency | `backend/tasks/views.py` | Listing 20 tasks caused more than 40 database queries (N+1 queries). | Accessing `assigned_to.username` and `created_by.username` in serializer without SQL joins. | Added `.select_related("assigned_to", "created_by")` to `TaskViewSet.get_queryset()`. | Yes |
| 11. Task Stats API (Part 2) | `backend/tasks/views.py` | Endpoint `GET /api/tasks/stats/` did not exist. | Part 2 feature requirement to provide user-specific stats summary. | Added `@action(detail=False)` `stats()` aggregating `todo`, `in_progress`, `done`, and `overdue` for `assigned_to=request.user` in 1 SQL query. | Yes |
| 12. Task Stats UI (Part 2) | `frontend/src/App.jsx`, `frontend/src/api.js`, `frontend/src/styles.css` | Summary bar not shown above task list. | Part 2 UI requirement to show 4 stats cards refreshing on user switch and mark done. | Implemented `fetchTaskStats()`, added summary bar above list, and hooked refresh to `[user]` and `handleMarkDone`. | Yes |
| 13. Mark Done Button Visibility | `frontend/src/TaskItem.jsx`, `frontend/src/App.jsx` | Users saw "Mark done" on other people's tasks, causing 403 Forbidden errors when clicked. | UI did not check whether logged-in user had edit permissions before rendering the button. | Computed `canEdit = currentUser && (task.assigned_to_name === currentUser \|\| task.created_by_name === currentUser)` to only display button to authorized users. | Yes |



## Feature: Task Stats (Part 2)
- Added `GET /api/tasks/stats/` endpoint returning `{"todo": n, "in_progress": n, "done": n, "overdue": n}` for tasks assigned to the current authenticated user.
- Overdue count properly excludes completed (`done`) tasks: `Q(due_date__lt=now) & ~Q(status="done")`.
- Frontend displays all 4 counts in a summary bar above the task list and dynamically refreshes when switching users or marking a task done.
- Added backend unit test `test_task_stats_for_logged_in_user` verifying correct counts, isolation per user, and execution in a single query.

### How many database queries does your endpoint run, and why?
- **1 query.**
- **Why:** It uses Django ORM's `.aggregate()` with conditional expressions (`Count("id", filter=Q(...))`) to calculate all four statistics (`todo`, `in_progress`, `done`, `overdue`) inside a single `SELECT COUNT(...)` SQL statement executed directly by the database engine.

## What would you improve with more time? (Part 3)
- Add full frontend pagination controls (Next/Previous page buttons) so users can browse beyond the first page of 20 tasks.
- Implement server-side sorting options in the UI (e.g., sort by priority, created date, or title).
- Replace HTTP Basic Authentication with modern JWT (JSON Web Tokens) or session cookies for production security.
- Add optimistic UI updates with automatic rollback on server error for instant feedback.
- Introduce client-side caching (e.g., TanStack React Query) to avoid refetching unchanged lists.

## Tradeoffs or assumptions you made
- Kept the existing demo HTTP Basic Authentication credentials (`username:password123`) to maintain zero breaking changes with the starter project setup.
- Assumed "overdue" strictly applies only to unfinished tasks (`todo` or `in_progress`) whose `due_date` is in the past, matching standard task tracking conventions.
- Maintained the 20-item page size from backend settings while displaying the true total count (`count`) in the header.

## Where did AI help you most, and where did it get something wrong?
- **Where AI helped most:** Rapidly identifying obscure edge cases like Django's SQLite `NULLS LAST` sorting behavior, diagnosing React's in-place state mutation preventing re-renders, and writing clean conditional SQL aggregations.
- **Where AI got something wrong:** In the first attempt at ordering, it referenced `models.F` without importing `models` directly in `views.py`, and initially evaluated date-only comparisons using deprecated `datetime.utcnow()` instead of Django's `timezone.now()`.

