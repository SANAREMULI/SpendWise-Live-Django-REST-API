# SpendWise Live API

A Django REST API for authenticated, per-user expense tracking.

## Setup

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

The API is available at `http://127.0.0.1:8000/api/`.

## Live dashboard

With the Django server running, open a second terminal and serve the dashboard:

```powershell
cd frontend
python -m http.server 5500
```

Open `http://127.0.0.1:5500`. Sign in with a Django user, add an expense, and it will appear immediately from the API. The All/Food/Transport/Bills buttons and search field reload the list using API query parameters. Use the Previous and Next controls to inspect paginated results.

## Authentication

POST credentials to `/api/login/` to receive a token:

```powershell
Invoke-RestMethod http://127.0.0.1:8000/api/login/ -Method Post -Body @{username='alice'; password='password123'}
```

Send it on every expense request as `Authorization: Token <token>`. The expense endpoint supports:

- `GET/POST /api/expenses/`
- `GET/PUT/PATCH/DELETE /api/expenses/<id>/`
- `?category=food`, `?search=coffee`, and `?ordering=-amount`
- page-number pagination with 10 records per page

Each user can only read and modify their own expenses. CORS is open for dashboard development; restrict `CORS_ALLOWED_ORIGINS` before production deployment.

## Tests

```powershell
python manage.py test
```

The test suite covers two-user isolation, automatic owner assignment, token and invalid-token authentication, category filtering, description search, amount ordering, and pagination metadata (`count`, `next`, `previous`, and `results`).

## Demo walkthrough

1. Create two users with `createsuperuser` and the Django shell, or use the admin.
2. Start Django and the static dashboard server.
3. Log in as the first user, add an expense, and show it appear without refreshing.
4. Log out, sign in as the second user, and show that the first user's expense is absent.
5. Use a category button and search term to show live filtering.

For submission evidence, capture the browser Network tab for the login and expense requests, plus terminal output from `python manage.py test`.