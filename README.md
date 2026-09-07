# LogShield

LogShield is a FastAPI service for authenticated log ingestion, indexed PostgreSQL telemetry, SQL-backed threat detection, and webhook-based SOAR-lite responses.

## Run with Docker Compose

```powershell
docker compose up --build
```

The API is available at `http://localhost:8000`, OpenAPI documentation is at `http://localhost:8000/docs`, and readiness checks are available at `http://localhost:8000/` and `http://localhost:8000/health`.

## API flow

1. Register or log in at `POST /api/v1/auth/register` or `POST /api/v1/auth/login`.
2. Send telemetry to `POST /api/v1/logs` with `X-API-Key` set to `INGESTION_API_KEY`.
3. Analysts and admins can list or resolve incidents with a JWT bearer token.
4. The scheduler evaluates brute-force and API-spike windows every 15 seconds and posts alert payloads to `WEBHOOK_URLS`.

## Local tests

Install `requirements.txt`, then run:

```powershell
python -m pytest
```

The tests use SQLite for isolation. Production runs use PostgreSQL and the declared composite and partial indexes.

## Run tests in Docker

With the Compose stack running in another terminal:

```powershell
docker compose exec api pytest
```
