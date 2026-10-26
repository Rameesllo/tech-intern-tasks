# Intern Tech Task — Task Tracker (60 minutes)

A small task tracker: **Django + DRF** backend, **React (Vite)** frontend.
The app *mostly* works, but it has several bugs. AI tools are allowed.

## Setup (≈5 min)
Backend (Python 3.10+):
```bash
cd backend
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py seed          # creates users alice, bob, carol (password: password123) + 30 tasks
python manage.py runserver     # http://localhost:8000/api/tasks/
```
Frontend (Node 18+):
```bash
cd frontend
npm install
npm run dev                    # http://localhost:5173
```
Run backend tests: `cd backend && python manage.py test`

## Expected behaviour
- The list shows tasks with assignee, status, and an **Overdue** badge when a not-done task is past its due date.
- The status filter shows only tasks with that status.
- "Mark done" updates the task immediately in the UI.
- **Only the assignee or the creator of a task may edit it. Only the creator may delete it.** Everyone may view all tasks.
- The creator of a task is always the user who created it; it cannot be set or changed by the client.
- Tasks are sorted by due date, soonest first; tasks with **no due date go last**.
- The count above the list shows the **total** number of tasks matching the current filter.
- The list endpoint should be efficient (no unnecessary database queries).

## Your tasks
### Part 1 — Fix bugs (~25 min)
Find and fix as many bugs as you can. There are about 10, in both backend and frontend; we don't expect you to find all of them, so prioritise.
For each fix, add one line to `NOTES.md`: **what was wrong and why** (root cause, not just "fixed it").

### Part 2 — Add a feature (~25 min)
Add **task stats for the current user**:
- Backend: `GET /api/tasks/stats/` returns, for tasks assigned to the logged-in user:
  `{"todo": n, "in_progress": n, "done": n, "overdue": n}`
- Frontend: show these counts in a summary bar above the list; it should update when the user switches or a task is marked done.
- Write at least one backend test for the endpoint.

*(Optional: build the Part 2 UI as a React Native / Expo screen instead.)*

### Part 3 — NOTES.md (~10 min)
- Your bug fixes (one line each)
- What you'd improve with more time
- Any tradeoffs or assumptions you made

## Submission
Push to a GitHub repo (or zip the folder, excluding `node_modules` and `.venv`) and share it before time is up.
