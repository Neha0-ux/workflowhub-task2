# WorkFlowHub

Minimal full-stack workflow app used to demonstrate CI/CD for SOFT806 Assignment 1 (Task 2).

- **Backend:** Django REST Framework (`backend/`): register, login, logout and CRUD for workflow items
- **Frontend:** React + Vite (`frontend/`)
- **Containers:** `backend/Dockerfile`, `frontend/Dockerfile`, `docker-compose.yml`
- **CI:** GitHub Actions (`.github/workflows/ci.yml`) and CircleCI (`.circleci/config.yml`)

## API

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/health/` | Health check |
| POST | `/api/auth/register/` | Create account `{username, email, password}` |
| POST | `/api/auth/login/` | Returns `{token, username}` |
| POST | `/api/auth/logout/` | Deletes the token |
| GET/POST | `/api/workflows/` | List (`?status=`) / create items |
| GET/PUT/PATCH/DELETE | `/api/workflows/{id}/` | Retrieve / edit / change status / delete |

## Environment variables

| Variable | Used by | Purpose |
|---|---|---|
| `DJANGO_SECRET_KEY` | backend | Secret key (stored as a CI secret) |
| `DJANGO_DEBUG` | backend | `True` only for local development |
| `DJANGO_ALLOWED_HOSTS` | backend | Allowed host names |
| `CORS_ALLOWED_ORIGINS` | backend | Frontend origins allowed to call the API |
| `VITE_API_URL` | frontend (build) | API base URL |

## Run with Docker

```bash
docker compose up --build
```

Frontend: http://localhost:3000 · API: http://localhost:8000/api/

## CI pipelines

Both pipelines run on every push and pull request: they install backend dependencies with pip, run the Django tests, and build the backend and frontend Docker images.
