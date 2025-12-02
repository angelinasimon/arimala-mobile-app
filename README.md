# arimala-mobile-app

Backend + mobile scaffolding for Arimala's check-in system.

## Backend setup

1. **Prerequisites**
   - Python 3.11+
   - [Poetry or pip + venv](https://docs.python.org/3/tutorial/venv.html)
   - Docker (for the local Postgres container)

2. **Bootstrap the environment**
   ```pwsh
   cd backend
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   copy .env.example .env  # then fill PASSKIT + DATABASE values
   ```

3. **Start Postgres locally**
   ```pwsh
   docker compose up -d postgres
   ```

4. **Apply migrations**
   ```pwsh
   cd backend
   alembic upgrade head
   ```
   The shipped revisions under `backend/alembic/versions/` create the `events`, `members`, `scans`, and
   `guest_details` tables (plus supporting enums) so a fresh developer can get a working schema immediately.

5. **Run the API**
   ```pwsh
   uvicorn app.main:app --reload --app-dir backend/app
   ```

6. **Execute the FastAPI test suite**
   ```pwsh
   $env:PYTHONPATH="backend"
   pytest backend/tests
   ```
   Tests stub PassKit responses by default and use a local SQLite DB (`test.db`). Delete the file if you
   need a clean run.

## Key backend capabilities

- Scan API validates event/member IDs, enforces duplicate detection, and records guest counts plus optional guest details (names/contact info) per scan.
- Configurable membership guest limits via `app/core/config.py` guard against over-capacity check-ins.
- `/events` endpoint supports `active_only` filters so the iOS scanner can pick current events only.
- `/dashboard/events/{event_id}/summary` aggregates totals and membership breakdowns for the admin dashboard.
- Alembic migrations provision all persistence tables (events, members, scans, guest_details) for Postgres or SQLite test environments.
