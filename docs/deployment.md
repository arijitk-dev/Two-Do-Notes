# Production deployment

Two Do Notes is prepared for this manual deployment topology:

- Frontend: Vercel, built from `frontend/`
- Backend: Render, built from `backend/` or the backend Dockerfile
- Database: Neon PostgreSQL
- Production branch: `prod`

No provider account, secret, or deployment is created by this repository.

## 1. GitHub

Push the repository to GitHub and keep the existing branch strategy:

- `main`: development/integration
- `fix`: fixes
- `prod`: production deployment source

Create or update `prod` deliberately after the checks below pass. Do not commit `.env` files or provider credentials.

## 2. Neon

Create a PostgreSQL database and copy its connection string into the Render `DATABASE_URL` environment variable. The application accepts standard `postgresql://`, `postgres://`, and `postgresql+psycopg://` forms and normalizes them to the installed psycopg driver. Use a Neon pooled connection string for the runtime if that is the connection string recommended by Neon; the application uses conservative SQLAlchemy pooling.

## 3. Render

Create a web service from the `prod` branch. Set the root directory to `backend/` if deploying from source, install `backend/requirements.txt`, and use:

```bash
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

Run the migration before starting the service:

```bash
alembic upgrade head
```

The backend Dockerfile also provides a production-compatible command that runs migrations and binds to Render's `PORT`.

Required Render variables:

```text
DATABASE_URL=postgresql+psycopg://...
JWT_SECRET=<long-random-secret>
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
DEFAULT_TIMEZONE=Asia/Kolkata
CORS_ORIGINS=https://<your-vercel-domain>
ENVIRONMENT=production
```

Set a health check path of `/health`. It returns `{"status":"ok"}` without exposing database details or secrets.

## 4. Vercel

Create a project from the same repository and set the root directory to `frontend/`. Use the standard Vite build command:

```bash
npm run build
```

Set the output directory to `dist` and configure:

```text
VITE_API_BASE_URL=https://<your-render-service>.onrender.com/api/v1
```

`vercel.json` keeps direct SPA routes such as `/todos` working. After the Vercel domain is known, put its exact origin in Render's `CORS_ORIGINS` value. Include multiple origins as a comma-separated list only when they are genuinely required.

## 5. Smoke test

After both providers are live:

1. `GET https://<render-service>.onrender.com/health` and confirm HTTP 200.
2. Open the Vercel URL and register a test account.
3. Log in and create a Todo.
4. Complete it and confirm the expected point transaction.
5. Check `/todos`, calendar, history/reuse, Daily Review, accountability, and Notes.
6. Confirm browser requests use the Render API URL and no CORS errors appear.

Production database backups and point-in-time recovery are managed by Neon. Do not treat application-level exports as a replacement for provider backups.
