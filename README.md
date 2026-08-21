# Two Do Notes

Two Do Notes is a personal productivity and accountability app built around a simple promise: plan honestly, do what you planned, and be accountable when you do not.

## Phase 1 and Phase 2 scope

This implementation includes registration/login, timezone-aware scheduled Todos, completion and missed-task ledger transactions, streaks, Notes, dashboard summaries, responsive browser UI, and Docker Compose development. Phase 2 adds a month calendar, date filtering, future planning, +2 points for a Todo first planned for tomorrow, and explicit selected-Todo carry-forward with a one-time +1 completion bonus. Phase 3 adds truthful completion/miss confirmation, optional Daily Reviews, formal successful-day streaks, planning accuracy, carry-forward and missed-reason analysis, point breakdowns, overplanning detection, and an accountability page. The Todo add-on makes the default Todo view today-first and adds a bounded history/reuse workflow.

## Architecture

The backend is a modular FastAPI application. Routes are thin and delegate business rules to services; SQLAlchemy models provide persistence; Alembic owns schema changes. The point ledger is the source of truth for totals, and `StreakService` owns the daily-success rule so it can evolve in a later phase. Every query is scoped to the authenticated user.

```
backend/app/{api,core,db,models,schemas,repositories,services}
frontend/src/{App.tsx,api.ts,components.tsx,layout.tsx,styles.css}
backend/alembic/versions/{0001_initial,0002_phase2_planning_carry_forward,0003_phase3_accountability,0004_todo_history_reuse}.py
docker-compose.yml
```

## Run with Docker

Prerequisites: Docker Desktop with Compose.

```bash
cp .env.example .env
docker compose up --build
```

Open <http://localhost:5173>. The API is at <http://localhost:8000>, Swagger is at <http://localhost:8000/docs>, and ReDoc is at <http://localhost:8000/redoc>. Compose runs `alembic upgrade head` before starting the API.

## Local development

For the backend, use Python 3.12+, create a virtual environment, install `backend/requirements.txt`, and run from `backend/`:

```bash
alembic upgrade head
uvicorn app.main:app --reload
```

Without `DATABASE_URL`, the backend uses a local SQLite database for convenience. Set `DATABASE_URL` to PostgreSQL when running against Postgres. For the frontend, use Node 20+:

```bash
cd frontend
npm install
npm run dev
```

## Tests

```bash
cd backend && pytest
cd frontend && npm test
```

Backend tests use isolated SQLite and cover authentication, protection, ownership, Todo CRUD actions, idempotent points, missed reasons, streak initialization, Notes, today defaults, 15-day history, and safe reuse. Frontend tests use Vitest and React Testing Library.

## Phase 2 rules

- Creating a Todo scheduled for the user’s next local calendar date awards exactly `+2` through the existing point ledger. Editing or rescheduling that Todo never awards another planning transaction.
- Carry-forward is never automatic. From the dashboard, review today’s pending Todos and move only the selected items to tomorrow. Moving awards no points.
- A carried Todo keeps its original date, records the date it was carried from, and increments its carry count. Its first successful completion awards the normal `+3` and one separate `+1 CARRY_FORWARD_BONUS`, even if it is carried more than once.
- Completed and missed Todos cannot be carried forward. Completing and missing remain limited to the user’s local today, and all calendar/tomorrow calculations use calendar-date arithmetic in the stored timezone.

Phase 2 API additions include `GET /api/v1/calendar?year=YYYY&month=M`, `GET /api/v1/todos?date=YYYY-MM-DD`, `GET /api/v1/todos/unresolved`, `POST /api/v1/todos/carry-forward`, and `POST /api/v1/todos/{todo_id}/carry-forward`.

## Phase 3 rules

- Completion requires an explicit truthful confirmation in the UI; the backend remains the authority and awards exactly +3 once.
- Missing requires a reason and awards exactly -7 once. Supported reason codes are `not_enough_time`, `unexpected_work`, `lost_focus`, `too_difficult`, `poor_planning`, and `other`.
- A successful day has at least one planned Todo, every planned Todo resolved as completed, missed, or carried forward, and a completion rate of at least 80%. Carried-forward and missed Todos are resolved but are not completed.
- An empty day is neutral and does not add a streak day. Existing calendar-gap behavior remains explicit: a gap separates streak runs.
- Daily Reviews are optional reflections. They never award or remove points and can be created or updated for historical dates owned by the user.
- Accountability metrics are derived from Todo state and the immutable point ledger. The rolling 7-day view warns when average planning is at least five Todos per day and completion is below 70%.

Phase 3 API additions include `GET /api/v1/accountability?range=today|7d|month`, `GET /api/v1/reviews/{date}`, `POST /api/v1/reviews/{date}`, and `PATCH /api/v1/reviews/{date}`.

## Todo history and reuse rules

- `GET /api/v1/todos` without a date returns only the user's local today. `?date=YYYY-MM-DD` remains available for explicit calendar dates; `start_date` and `end_date` are database-filtered range queries.
- `GET /api/v1/todos/history` returns today plus the prior 14 calendar days (15 dates total). It supports an optional title/description search.
- `POST /api/v1/todos/{todo_id}/reuse` and `POST /api/v1/todos/reuse` create new pending Todos for today by copying only title, description, and priority. Reuse awards no points; later completion uses the normal +3 rule. New rows keep `source_todo_id` for auditability.
- Equivalent same-day Todos are not duplicated. Bulk reuse skips equivalent items; single-item reuse reports a conflict so the UI can say the Todo is already on today's list.
- The 15-day limit is enforced server-side for the normal history/reuse interface. Older Todo rows are not automatically hard-deleted, because canonical Todo state and the immutable point ledger remain auditable for accountability and streak calculations.

## Environment variables

See [.env.example](.env.example). `JWT_SECRET` must be replaced for any non-local deployment. `DEFAULT_TIMEZONE` defaults to `Asia/Kolkata`, but all “today” calculations read the user timezone rather than embedding that value in business logic.

## Future phases

Later phases can add rewards, reminders, notifications, PWA support, and Android without changing the ledger or route/service boundaries.
