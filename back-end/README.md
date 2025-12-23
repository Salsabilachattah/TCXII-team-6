# TCXII-team-6 Backend

This repo contains a FastAPI backend for a ticketing system with role-based access (client, agent, admin). It uses SQLAlchemy with MySQL, JWT auth, and Pydantic schemas.

## Core features
- Auth: register, login, refresh, logout, change password; password hashing; JWT access + refresh tokens.
- User profile: get current user, update profile fields, deactivate/reactivate account, delete account.
- Ticketing (client/admin): create tickets, list with pagination, view detail, submit feedback after response.
- Ticketing (agent/admin): list all tickets, search/filter, view detail, respond to tickets, mark processed, escalate.
- Ticket reference IDs: category prefix + year + numeric id (e.g., FAQ-2024-000123).
- Category validation: allowed categories are `guide`, `faq`, `policies`, `general`.
- Dashboard analytics: totals, pending/processed, escalation and satisfaction rates, alerts, category breakdown, agent performance.
- RBAC: role checks via dependencies on protected endpoints.
- Startup bootstrap: auto-creates tables on app startup; permissive CORS for dev/hackathon.

## API overview (base: `/api`)
Auth
- POST `/auth/register`
- POST `/auth/login`
- POST `/auth/refresh`
- POST `/auth/logout`
- POST `/auth/change-password`

Users
- GET `/users/me`
- PATCH `/users/me`
- POST `/users/Desactiver-compte`
- POST `/users/Reactiver-compte`
- DELETE `/users/delete-account`

Tickets (client/admin)
- POST `/tickets`
- GET `/tickets/list`
- GET `/tickets/{ticket_id}`
- POST `/tickets/{ticket_id}/feedback`

Tickets (agent/admin)
- GET `/tickets/agent/list`
- GET `/tickets/agent/search`
- GET `/tickets/agent/{ticket_id}`
- POST `/tickets/agent/{ticket_id}/response`
- POST `/tickets/agent/{ticket_id}/escalate`

Admin
- POST `/admin/agents`

Dashboard
- GET `/dashboard/stats`
- GET `/dashboard/detailed-metrics`
- GET `/dashboard/alerts`
- GET `/dashboard/category-breakdown`
- GET `/dashboard/agent-performance`

## Configuration
Env vars in `.env` (see `back-end/app/core/config.py`):
- APP_NAME, ENV
- DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME
- SECRET_KEY, ACCESS_TOKEN_EXPIRE_MINUTES, REFRESH_TOKEN_EXPIRE_DAYS
- SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASSWORD, EMAIL_FROM (reserved for email integrations)
- APP_URL (optional)

## Run locally
1) Go to the backend folder:
```
cd back-end
```
2) Create and activate a virtual environment:
```
python -m venv .venv
```
Windows (PowerShell):
```
.\.venv\Scripts\Activate
```
macOS/Linux:
```
source .venv/bin/activate
```
3) Install dependencies:
```
pip install -r requirements.txt
```
4) Create `back-end/.env` and fill the variables listed in the Configuration section.
5) Run the API:
```
uvicorn app.main:app --reload
```
Open `http://localhost:8000/docs` for Swagger UI.

## Key directories
- `back-end/app/api`: route groups and controllers
- `back-end/app/models`: SQLAlchemy models
- `back-end/app/schemas`: Pydantic schemas
- `back-end/app/core`: config, db, security, roles/permissions
- `back-end/app/features/ticket_reference`: ticket reference generator
