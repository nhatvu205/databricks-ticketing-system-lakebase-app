# Lakebase Support Ticketing App

A small internal-support application built with Flask, Databricks Apps, and Lakebase Autoscaling PostgreSQL. It stores tickets and ticket messages in Lakebase, not in application memory or hard-coded data.

## Features

- View and filter tickets by status.
- View a ticket's complete message history.
- Create a ticket with priority.
- Add messages and update ticket status.
- Show live ticket statistics.
- Seed three tickets with two messages each on the first deployment.
- Use the Databricks App service principal and rotating OAuth database credentials; no password is committed.

## Local checks

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements-dev.txt
python -m pytest
```

The unit tests run without a database. To run the PostgreSQL integration test, set `TEST_DATABASE_URL` to a disposable PostgreSQL database before invoking `pytest`.

## Deploy to Databricks

Read [docs/DATABRICKS_DEPLOYMENT.md](docs/DATABRICKS_DEPLOYMENT.md) for the exact Free Edition setup and deployment steps. The only deployment-specific setting in `app.yaml` is `LAKEBASE_ENDPOINT`, resolved from the Lakebase app resource key `postgres`.

## Submission artifacts

Use the following files before submitting:

- [docs/SUBMISSION_CHECKLIST.md](docs/SUBMISSION_CHECKLIST.md)
- [docs/REFLECTION_DRAFT.md](docs/REFLECTION_DRAFT.md)
- `python scripts/package_submission.py`
