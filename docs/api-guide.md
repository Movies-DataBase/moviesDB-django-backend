# UserAuth API Guide

Base URL prefix: `/userAuth/`

All protected routes require the header:

```
Authorization: Bearer <token>
```

---

## 1. Check Username

Check if a username is already taken.

- **Method:** `GET`
- **URL:** `/userAuth/check-username/?username=admin`
- **Auth Required:** No

**Sample Response — username exists:**

```json
{
  "exists": true,
  "username": "admin"
}
```

**Sample Response — username does not exist:**

```json
{
  "exists": false,
  "username": "ghost"
}
```

---

## 2. Check Email

Check if an email is already registered.

- **Method:** `GET`
- **URL:** `/userAuth/check-email/?email=admin@example.com`
- **Auth Required:** No

**Sample Response — email exists:**

```json
{
  "exists": true,
  "email": "admin@example.com"
}
```

**Sample Response — email does not exist:**

```json
{
  "exists": false,
  "email": "new@example.com"
}
```

---

## 3. Signup

Create a new user account.

- **Method:** `POST`
- **URL:** `/userAuth/signup/`
- **Auth Required:** No
- **Content-Type:** `application/json`

**Request Body:**

```json
{
  "username": "john",
  "email": "john@example.com",
  "password": "secret123"
}
```

**Sample Response (201):**

```json
{
  "message": "Account created successfully.",
  "user_id": "6999a875dda35d0ec3213b02",
  "username": "john",
  "email": "john@example.com"
}
```

**Error — username taken (409):**

```json
{
  "error": "Username already taken."
}
```

**Error — email registered (409):**

```json
{
  "error": "Email already registered."
}
```

---

## 4. Login

Authenticate a user and receive a JWT token.

- **Method:** `POST`
- **URL:** `/userAuth/login/`
- **Auth Required:** No
- **Content-Type:** `application/json`

**Request Body:**

```json
{
  "username": "john",
  "password": "secret123"
}
```

**Sample Response (200):**

```json
{
  "message": "Login successful.",
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "username": "john",
  "email": "john@example.com",
  "is_admin": false
}
```

**Error — wrong credentials (401):**

```json
{
  "error": "Invalid username or password."
}
```

---

## 5. Logout

Invalidate the current JWT token.

- **Method:** `POST`
- **URL:** `/userAuth/logout/`
- **Auth Required:** Yes

**Request Header:**

```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Sample Response (200):**

```json
{
  "message": "Logged out successfully."
}
```

---

## 6. Get Profile

Fetch the authenticated user's profile.

- **Method:** `GET`
- **URL:** `/userAuth/profile/`
- **Auth Required:** Yes

**Request Header:**

```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Sample Response (200):**

```json
{
  "user": {
    "username": "john",
    "email": "john@example.com",
    "is_admin": false,
    "created_at": "2026-02-21T10:30:00.000000"
  }
}
```

---

## 7. Update Profile

Update the authenticated user's username or email.

- **Method:** `PUT`
- **URL:** `/userAuth/profile/update/`
- **Auth Required:** Yes
- **Content-Type:** `application/json`

**Request Header:**

```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Request Body (any or both fields):**

```json
{
  "username": "john_new",
  "email": "john_new@example.com"
}
```

**Sample Response (200):**

```json
{
  "message": "Profile updated successfully.",
  "updated_fields": {
    "username": "john_new",
    "email": "john_new@example.com"
  }
}
```

**Error — username/email already in use (409):**

```json
{
  "error": "Username already taken."
}
```

---

## 8. Change Password

Change the authenticated user's password.

- **Method:** `PUT`
- **URL:** `/userAuth/change-password/`
- **Auth Required:** Yes
- **Content-Type:** `application/json`

**Request Header:**

```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Request Body:**

```json
{
  "old_password": "secret123",
  "new_password": "newSecret456"
}
```

**Sample Response (200):**

```json
{
  "message": "Password changed successfully."
}
```

**Error — wrong old password (401):**

```json
{
  "error": "Old password is incorrect."
}
```

---

## Common Error Responses

| Status | Meaning                          |
| ------ | -------------------------------- |
| 400    | Bad request / missing fields     |
| 401    | Unauthorized / wrong credentials |
| 404    | Resource not found               |
| 405    | Method not allowed               |
| 409    | Conflict (duplicate data)        |

---

## Token Notes

- Tokens expire after **24 hours**.
- Logged-out tokens are **blacklisted** in the `token_blacklist` MongoDB collection and cannot be reused.
- Always store tokens securely (e.g., in memory or a secure HTTP-only cookie — never in `localStorage` for sensitive apps).
