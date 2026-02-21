# GitHub Copilot Instructions

## Project Overview

This is a Django backend project with MongoDB (Atlas) as the database.
The user authentication system lives in `djangoBackend/userAuth/`.

---

## API Documentation Rule (CRITICAL)

**Whenever you make any change to an API — including but not limited to:**

- Adding a new endpoint
- Removing an existing endpoint
- Changing a request method (GET, POST, PUT, etc.)
- Changing the request body structure or fields
- Changing the response body structure or fields
- Adding or removing authentication requirements
- Changing URL paths
- Changing error response formats or status codes

**You MUST update `docs/api-guide.md` to reflect those changes immediately.**

This file is the single source of truth for API consumers (frontend devs, mobile devs, testers).
Do not leave it out of sync with the actual code.

---

## Project Structure

```
djangoBackend/
  manage.py
  moviesDB/           # Django project settings, root urls.py
    settings.py
    urls.py           # Root URL config — all auth routes use /userAuth/ prefix
  userAuth/           # User authentication app
    views.py          # All API view functions
    urls.py           # URL patterns for userAuth app
    models.py
docs/
  api-guide.md        # <-- ALWAYS keep this updated when APIs change
djangovenv/           # Python virtual environment
```

---

## Tech Stack

- **Framework:** Django 6.x
- **Database:** MongoDB Atlas via `pymongo`
- **Auth:** JWT (`PyJWT`) with bcrypt password hashing
- **DB Name:** `moviesDB`
- **Collections:** `users`, `token_blacklist`

---

## Coding Conventions

- All views use plain Django function-based views (no DRF).
- CSRF is disabled on mutating endpoints via `@csrf_exempt`.
- Protected routes use the `_require_auth(request)` helper.
- Passwords are hashed with `bcrypt` before storing.
- JWT tokens expire in 24 hours and are blacklisted on logout.
- The URL prefix for userAuth is `/userAuth/` (defined in `moviesDB/urls.py`).

---

## Adding a New API Checklist

1. Implement the view function in `userAuth/views.py`.
2. Register the URL in `userAuth/urls.py`.
3. **Update `docs/api-guide.md`** with:
   - Method, URL, auth requirement
   - Request body (if applicable)
   - Sample success response
   - Sample error responses
