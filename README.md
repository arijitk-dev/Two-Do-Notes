# Two Do Notes

Two Do Notes is a personal productivity and accountability app built around a simple promise: plan honestly, do what you planned, and be accountable when you do not.

## Phase 1 and Phase 2 scope

This implementation includes registration/login, timezone-aware scheduled Todos, completion and missed-task ledger transactions, streaks, Notes, dashboard summaries, responsive browser UI, and Docker Compose development. Phase 2 adds a month calendar, date filtering, future planning, +2 points for a Todo first planned for tomorrow, and explicit selected-Todo carry-forward with a one-time +1 completion bonus.

## Architecture

The backend is a modular FastAPI application. Routes are thin and delegate business rules to services; SQLAlchemy models provide persistence; Alembic owns schema changes. The point ledger is the source of truth for totals, and `StreakService` owns the daily-success rule so it can evolve in a later phase. Every query is scoped to the authenticated user.

```
backend/app/{api,core,db,models,schemas,repositories,services}
frontend/src/{App.tsx,api.ts,components.tsx,layout.tsx,styles.css}
backend/alembic/versions/{0001_initial,0002_phase2_planning_carry_forward}.py
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

Backend tests use isolated SQLite and cover authentication, protection, ownership, Todo CRUD actions, idempotent points, missed reasons, streak initialization, and Notes. Frontend tests use Vitest and React Testing Library.

## Phase 2 rules

- Creating a Todo scheduled for the user’s next local calendar date awards exactly `+2` through the existing point ledger. Editing or rescheduling that Todo never awards another planning transaction.
- Carry-forward is never automatic. From the dashboard, review today’s pending Todos and move only the selected items to tomorrow. Moving awards no points.
- A carried Todo keeps its original date, records the date it was carried from, and increments its carry count. Its first successful completion awards the normal `+3` and one separate `+1 CARRY_FORWARD_BONUS`, even if it is carried more than once.
- Completed and missed Todos cannot be carried forward. Completing and missing remain limited to the user’s local today, and all calendar/tomorrow calculations use calendar-date arithmetic in the stored timezone.

Phase 2 API additions include `GET /api/v1/calendar?year=YYYY&month=M`, `GET /api/v1/todos?date=YYYY-MM-DD`, `GET /api/v1/todos/unresolved`, `POST /api/v1/todos/carry-forward`, and `POST /api/v1/todos/{todo_id}/carry-forward`.

## Environment variables

See [.env.example](.env.example). `JWT_SECRET` must be replaced for any non-local deployment. `DEFAULT_TIMEZONE` defaults to `Asia/Kolkata`, but all “today” calculations read the user timezone rather than embedding that value in business logic.

## Future phases

Later phases can add rewards, analytics, daily review, reminders, notifications, PWA support, and Android without changing the ledger or route/service boundaries.
