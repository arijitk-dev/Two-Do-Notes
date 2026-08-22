# Phase 6A: Daily 10 AM Todo Reminder Email

## Overview

Phase 6A implements an automated daily reminder email that sends to users at approximately 10:00 AM Asia/Kolkata (04:30 UTC). The email reminds users to intentionally plan or check their Todos for the day, reinforcing the core philosophy of the application.

## Architecture

The implementation uses a clean, simple architecture:

```
GitHub Actions (scheduler)
    ↓
daily-todo-reminder.yml (cron: 30 4 * * *)
    ↓
POST /internal/jobs/daily-todo-reminder
    ↓
FastAPI Backend
    ↓
DailyReminderEmailService
    ↓
Email Delivery Log (idempotency)
    ↓
Neon PostgreSQL
    ↓
Resend (email provider)
    ↓
User Email
```

**Key Design Principles:**

- GitHub Actions only triggers the job; FastAPI owns all business logic
- No in-process scheduler (no APScheduler, Celery, Redis, etc.)
- Idempotent execution: safe to run twice
- Timezone-aware: uses user's configured timezone
- Graceful failure: one user's email failure doesn't block others

## Files Created

1. **[backend/app/models/email_delivery_log.py](backend/app/models/email_delivery_log.py)**
   - `EmailDeliveryLog` model for tracking sent/failed emails
   - Enums: `EmailType` (DAILY_TODO_REMINDER), `EmailStatus` (SENT, FAILED, PENDING)
   - Unique constraint on (user_id, email_type, scheduled_date) for idempotency

2. **[backend/app/services/daily_reminder_email_service.py](backend/app/services/daily_reminder_email_service.py)**
   - `DailyReminderEmailService` class with static methods:
     - `validate_timezone()` - IANA timezone validation
     - `get_today_date_for_user()` - Get date in user's timezone
     - `check_email_already_sent()` - Idempotency check
     - `get_user_todos_for_today()` - Query today's todos
     - `send_email_via_resend()` - Send via Resend API
     - `create_email_log()` - Log delivery result
     - `process_daily_reminders()` - Main job orchestration

3. **[backend/app/api/internal.py](backend/app/api/internal.py)**
   - Internal API endpoints for scheduled jobs
   - `POST /internal/jobs/daily-todo-reminder` - Protected by CRON_SECRET

4. **[.github/workflows/daily-todo-reminder.yml](.github/workflows/daily-todo-reminder.yml)**
   - GitHub Actions workflow
   - Scheduled: `30 4 * * *` (04:30 UTC = 10:00 AM IST)
   - Supports `workflow_dispatch` for manual testing
   - Calls internal endpoint with CRON_SECRET

5. **[backend/alembic/versions/0004_email_delivery_logs.py](backend/alembic/versions/0004_email_delivery_logs.py)**
   - Alembic migration for email_delivery_logs table
   - Unique constraint ensures idempotency

6. **[backend/tests/test_phase6a_daily_reminder.py](backend/tests/test_phase6a_daily_reminder.py)**
   - 17 comprehensive tests covering:
     - Timezone validation (valid/invalid)
     - Idempotency protection
     - Email delivery mocking
     - Secret validation
     - Todo querying
     - Database logging

## Files Modified

1. **[backend/app/core/config.py](backend/app/core/config.py)**
   - Added settings:
     - `resend_api_key` - Resend API key
     - `email_from` - Sender email address
     - `frontend_url` - URL for email links
     - `cron_secret` - Secret for internal jobs

2. **[backend/app/main.py](backend/app/main.py)**
   - Imported internal API router
   - Registered internal router (no prefix)

3. **[backend/app/models/**init**.py](backend/app/models/__init__.py)**
   - Exported EmailDeliveryLog

4. **[backend/requirements.txt](backend/requirements.txt)**
   - Added `resend==0.8.0`

5. **[.env.example](.env.example)** and **[backend/.env.example](backend/.env.example)**
   - Added configuration placeholders:
     - RESEND_API_KEY=
     - EMAIL_FROM=
     - FRONTEND_URL=
     - CRON_SECRET=

## Security Implementation

### CRON_SECRET Protection

- Stored as environment variable on Render backend
- Stored as GitHub Actions secret
- Validated on every request to `/internal/jobs/daily-todo-reminder`
- Missing or incorrect secret returns 401/403
- Never logged or exposed in responses

### API Security

- Internal endpoint not protected by JWT (uses CRON_SECRET instead)
- No sensitive data in response (no user emails, todos, or secrets)
- Header-based authentication using X-Cron-Secret

### Data Security

- Email addresses never logged
- Todo contents never logged
- API keys never logged or exposed
- Timezone values validated before use

## Timezone Implementation

### Validation

All user timezones are validated using Python's `zoneinfo`:

```python
def validate_timezone(timezone_str: str) -> bool:
    """Validate timezone string against IANA timezone database."""
    try:
        ZoneInfo(timezone_str)
        return True
    except Exception:
        return False
```

### Invalid Timezone Handling

- If a user has an invalid timezone (e.g., "string"), the service:
  1. Logs a warning (without sensitive data)
  2. Uses UTC as fallback for that execution only
  3. Does NOT modify the database
  4. Does NOT crash the job

This prevents the "RangeError: Invalid time zone specified: string" incident.

## Idempotency Implementation

### Database-Level Protection

The email_delivery_logs table has a unique constraint:

```python
UniqueConstraint('user_id', 'email_type', 'scheduled_date',
                 name='uq_email_delivery_logs_user_type_date')
```

This ensures only one email of a given type can be recorded per user per date.

### Process Flow

1. Check if email already sent for today (SELECT)
2. If already sent, skip user (return "skipped")
3. If not sent, send email via Resend
4. Create delivery log entry with atomic INSERT or constraint violation

### Duplicate Execution Safety

If GitHub Actions accidentally triggers twice:

- First execution sends email, creates log entry
- Second execution checks log, finds sent entry, skips user
- No duplicate emails sent

## Email Content

### Subject

```
🌅 Good morning — what's your plan today?
```

### Body Format

Both HTML and plain-text versions are sent:

**HTML:** Professional, styled email with:

- Greeting
- User's todo count and completion status
- Core philosophy reminder
- Clickable button linking to /todos

**Plain Text:** Fallback for email clients without HTML support

### Dynamic Content

- **Todo Count:** "0 planned" vs "4 planned"
- **Completion Status:** "0 completed" vs "2 of 4 completed"
- **Frontend URL:** Configurable, defaults to FRONTEND_URL env var

## Logging and Observability

### Logged (Safe)

```
- job started
- number of users considered
- number sent/skipped/failed
- job completed
```

### NOT Logged (Security)

```
- email addresses
- todo contents
- API keys or secrets
- user IDs (only in error context)
```

### Example Log Output

```
INFO     app.services.daily_reminder_email_service Found 2 users
INFO     app.services.daily_reminder_email_service Email sent to user abc123
INFO     app.services.daily_reminder_email_service Job completed: {
           "processed": 2,
           "sent": 1,
           "skipped": 1,
           "failed": 0
        }
```

## Test Results

All 31 backend tests pass:

```
======================== 31 passed, 2 warnings in 12.22s ========================
```

### Phase 6A Specific Tests (17 tests)

✅ Timezone validation (valid/invalid)
✅ Date calculation for different timezones
✅ Idempotency checks
✅ Email delivery tracking
✅ Secret validation (missing/invalid/valid)
✅ Todo query
✅ Duplicate prevention
✅ API endpoint authorization
✅ Response format and stats

## Environment Configuration

### Local Development (.env)

```dotenv
RESEND_API_KEY=                    # Leave empty for local dev
EMAIL_FROM=noreply@two-do-notes.com
FRONTEND_URL=http://localhost:5173
CRON_SECRET=your-test-secret       # Use any value locally
```

### Render Production Environment Variables

Add these manually to Render dashboard:

```
RESEND_API_KEY=re_xxx...           # From Resend.com
EMAIL_FROM=noreply@your-domain.com # Your verified domain
FRONTEND_URL=https://two-do-notes.vercel.app
CRON_SECRET=secure-random-string   # Generate secure value
```

### GitHub Actions Secrets

Add these manually to GitHub repository secrets:

```
CRON_SECRET                         # Must match Render value
RENDER_DAILY_REMINDER_URL           # e.g., https://api.your-render.app
```

## Local Testing

### Test 1: Timezone Validation

```python
python -c "
from app.services.daily_reminder_email_service import DailyReminderEmailService
assert DailyReminderEmailService.validate_timezone('Asia/Kolkata')
assert DailyReminderEmailService.validate_timezone('InvalidTimezone') == False
print('✓ Timezone validation works')
"
```

### Test 2: API Endpoint

```bash
# Start backend
cd backend
python -m uvicorn app.main:app --reload

# Test valid secret (in another terminal)
curl -X POST http://localhost:8000/internal/jobs/daily-todo-reminder \
  -H "X-Cron-Secret: test-secret"

# Test invalid secret (should return 403)
curl -X POST http://localhost:8000/internal/jobs/daily-todo-reminder \
  -H "X-Cron-Secret: wrong-secret"

# Test missing secret (should return 401)
curl -X POST http://localhost:8000/internal/jobs/daily-todo-reminder
```

### Test 3: Idempotency

Run the endpoint twice and verify:

- First execution: "sent": 1
- Second execution: "skipped": 1 (no duplicate sent)

## GitHub Actions Testing

### Manual Trigger

1. Go to: Actions → Daily Todo Reminder
2. Click "Run workflow"
3. Check logs in GitHub Actions
4. Verify email was received

### Limitations

- GitHub Actions scheduling not guaranteed to exact time
- Small delays due to:
  - GitHub Actions queueing
  - Render cold start (may sleep if inactive)
  - Resend API latency
- Target: ~10:00 AM IST, actual: ±5 minutes

## Known Limitations

1. **Email Timing:** Not guaranteed to exactly 10:00 AM. Could be delayed by GitHub Actions queuing, Render cold start, or Resend API latency.

2. **Single User Assumption:** Currently assumes single user (personal use). If scaled to multiple users, consider:
   - Email rate limits (Resend free tier: 100/day)
   - Batch processing for large user counts
   - Per-user rate limiting

3. **Render Free Tier:** Web service may sleep after 15 minutes of inactivity. GitHub Action calling the endpoint will wake it.

4. **No Retry Logic:** If Resend API fails, no automatic retry. Next scheduled run (tomorrow) will retry.

5. **No Email Template System:** Uses simple HTML/text generation. If email design becomes more complex, consider migrating to a template engine.

## AGENTS.md Update

The following architectural invariant should be noted in AGENTS.md:

> **Scheduled Jobs:** Scheduled jobs (daily email reminders, etc.) must be:
>
> - Triggered externally (GitHub Actions, not in-process scheduler)
> - Idempotent (safe to run multiple times)
> - Not rely on Render web service remaining continuously awake
> - Log minimally (no secrets, emails, or sensitive data)

## Promotion to Production

This implementation is **ready to promote main → prod** when:

✅ All tests pass (31/31)
✅ Local endpoint testing works
✅ Timezone validation prevents crashes
✅ Idempotency protection works
✅ CRON_SECRET properly validated
✅ No secrets committed
✅ prod branch untouched

### Promotion Checklist

Before running `git merge main → prod`:

1. Verify all tests pass: `pytest tests/`
2. Verify migrations run: `alembic upgrade head`
3. Verify GitHub Actions workflow syntax
4. Set up Render environment variables manually
5. Set up GitHub Actions secrets manually
6. Test GitHub Actions manual trigger
7. Verify duplicate protection (run twice, check logs)
8. Document any custom changes needed for production domain

## Support & Troubleshooting

### Email Not Received

- Check RESEND_API_KEY is valid and has quota
- Check EMAIL_FROM is verified on Resend
- Check user email is valid in database
- Check logs for Resend error response

### Duplicate Emails

- Check email_delivery_logs table for logs
- Verify unique constraint exists: `uq_email_delivery_logs_user_type_date`
- Next execution should skip (check "skipped" count)

### Wrong Email Time

- Check GitHub Actions cron is `30 4 * * *`
- Remember: GitHub Actions timing not guaranteed
- Check Render cold start time in logs
- Render dashboard shows execution times

### Invalid Timezone Error

- Service should gracefully fall back to UTC
- Check logs for warning (should NOT crash job)
- Consider updating user's timezone in database

## See Also

- [AGENTS.md](AGENTS.md) - Architecture and business rules
- [backend/tests/test_phase6a_daily_reminder.py](backend/tests/test_phase6a_daily_reminder.py) - Test examples
- [.github/workflows/daily-todo-reminder.yml](.github/workflows/daily-todo-reminder.yml) - Workflow definition
