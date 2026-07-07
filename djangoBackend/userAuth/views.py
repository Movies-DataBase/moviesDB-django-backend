import json
import os
import datetime
from pathlib import Path

import bcrypt
import jwt
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from pymongo import MongoClient

ENV_FILE = Path(__file__).resolve().parents[2] / ".env"


def _load_env():
    if not ENV_FILE.exists():
        return

    for line in ENV_FILE.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue

        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        os.environ.setdefault(key, value)


_load_env()

MONGO_URI = os.getenv("MONGO_URI", "")
JWT_SECRET = os.getenv("JWT_SECRET", "your-super-secret-jwt-key-change-in-production")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
JWT_EXPIRY_HOURS = int(os.getenv("JWT_EXPIRY_HOURS", "24"))

print(f"Loaded environment variables: MONGO_URI={MONGO_URI}, JWT_SECRET={'*' * len(JWT_SECRET)}, JWT_ALGORITHM={JWT_ALGORITHM}, JWT_EXPIRY_HOURS={JWT_EXPIRY_HOURS}")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def get_db():
    client = MongoClient(MONGO_URI)
    return client["moviesDB"]


def _get_token_from_header(request):
    """Extract Bearer token from Authorization header."""
    auth = request.headers.get("Authorization", "")
    if auth.startswith("Bearer "):
        return auth[7:]
    return None


def _decode_token(token):
    """Decode and validate JWT. Returns payload or raises jwt.PyJWTError."""
    db = get_db()
    if db["token_blacklist"].find_one({"token": token}):
        raise jwt.InvalidTokenError("Token has been logged out.")
    return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])


def _require_auth(request):
    """Returns (payload, None) or (None, JsonResponse error)."""
    token = _get_token_from_header(request)
    if not token:
        return None, JsonResponse({"error": "Authorization token missing."}, status=401)
    try:
        payload = _decode_token(token)
        return payload, None
    except jwt.ExpiredSignatureError:
        return None, JsonResponse({"error": "Token has expired."}, status=401)
    except jwt.PyJWTError as e:
        return None, JsonResponse({"error": str(e)}, status=401)


# ---------------------------------------------------------------------------
# Index
# ---------------------------------------------------------------------------

def index(request):
    return HttpResponse("Hello, world. You're at the userAuth index.")


# ---------------------------------------------------------------------------
# 1. Check Username
# ---------------------------------------------------------------------------

def check_username(request):
    """GET /userAuth/check-username/?username=<value>"""
    if request.method != "GET":
        return JsonResponse({"error": "Only GET method is allowed."}, status=405)

    username = request.GET.get("username", "").strip()
    if not username:
        return JsonResponse({"error": "'username' query parameter is required."}, status=400)

    db = get_db()
    user = db["users"].find_one({"username": username}, {"_id": 0, "username": 1})

    if user:
        return JsonResponse({"exists": True, "username": username})
    return JsonResponse({"exists": False, "username": username})


# ---------------------------------------------------------------------------
# 2. Check Email
# ---------------------------------------------------------------------------

def check_email(request):
    """GET /userAuth/check-email/?email=<value>"""
    if request.method != "GET":
        return JsonResponse({"error": "Only GET method is allowed."}, status=405)

    email = request.GET.get("email", "").strip().lower()
    if not email:
        return JsonResponse({"error": "'email' query parameter is required."}, status=400)

    db = get_db()
    user = db["users"].find_one({"email": email}, {"_id": 0, "email": 1})

    if user:
        return JsonResponse({"exists": True, "email": email})
    return JsonResponse({"exists": False, "email": email})


# ---------------------------------------------------------------------------
# 3. Signup
# ---------------------------------------------------------------------------

@csrf_exempt
def signup(request):
    """POST /userAuth/signup/"""
    if request.method != "POST":
        return JsonResponse({"error": "Only POST method is allowed."}, status=405)

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON body."}, status=400)

    username = data.get("username", "").strip()
    email = data.get("email", "").strip().lower()
    password = data.get("password", "")

    if not username or not email or not password:
        return JsonResponse({"error": "username, email, and password are required."}, status=400)

    db = get_db()

    if db["users"].find_one({"username": username}):
        return JsonResponse({"error": "Username already taken."}, status=409)

    if db["users"].find_one({"email": email}):
        return JsonResponse({"error": "Email already registered."}, status=409)

    hashed_pw = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

    result = db["users"].insert_one({
        "username": username,
        "email": email,
        "password": hashed_pw,
        "is_admin": False,
        "created_at": datetime.datetime.utcnow().isoformat(),
    })

    return JsonResponse({
        "message": "Account created successfully.",
        "user_id": str(result.inserted_id),
        "username": username,
        "email": email,
    }, status=201)


# ---------------------------------------------------------------------------
# 4. Login
# ---------------------------------------------------------------------------

@csrf_exempt
def login(request):
    """POST /userAuth/login/"""
    if request.method != "POST":
        return JsonResponse({"error": "Only POST method is allowed."}, status=405)

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON body."}, status=400)

    username = data.get("username", "").strip()
    password = data.get("password", "")

    if not username or not password:
        return JsonResponse({"error": "username and password are required."}, status=400)

    db = get_db()
    user = db["users"].find_one({"username": username})

    if not user:
        return JsonResponse({"error": "Invalid username or password."}, status=401)

    stored_pw = user["password"]
    # Support both bcrypt-hashed and plain-text legacy passwords
    if stored_pw.startswith("$2b$") or stored_pw.startswith("$2a$"):
        match = bcrypt.checkpw(password.encode(), stored_pw.encode())
    else:
        match = (password == stored_pw)

    if not match:
        return JsonResponse({"error": "Invalid username or password."}, status=401)

    payload = {
        "user_id": str(user["_id"]),
        "username": user["username"],
        "is_admin": user.get("is_admin", False),
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=JWT_EXPIRY_HOURS),
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

    return JsonResponse({
        "message": "Login successful.",
        "token": token,
        "username": user["username"],
        "email": user["email"],
        "is_admin": user.get("is_admin", False),
    })


# ---------------------------------------------------------------------------
# 5. Logout
# ---------------------------------------------------------------------------

@csrf_exempt
def logout(request):
    """POST /userAuth/logout/  — requires Authorization: Bearer <token>"""
    if request.method != "POST":
        return JsonResponse({"error": "Only POST method is allowed."}, status=405)

    token = _get_token_from_header(request)
    if not token:
        return JsonResponse({"error": "Authorization token missing."}, status=401)

    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    except jwt.ExpiredSignatureError:
        return JsonResponse({"message": "Token already expired."})
    except jwt.PyJWTError as e:
        return JsonResponse({"error": str(e)}, status=401)

    db = get_db()
    db["token_blacklist"].insert_one({
        "token": token,
        "expired_at": datetime.datetime.utcfromtimestamp(payload["exp"]).isoformat(),
    })

    return JsonResponse({"message": "Logged out successfully."})


# ---------------------------------------------------------------------------
# 6. Get Profile
# ---------------------------------------------------------------------------

def get_profile(request):
    """GET /userAuth/profile/  — requires Authorization: Bearer <token>"""
    if request.method != "GET":
        return JsonResponse({"error": "Only GET method is allowed."}, status=405)

    payload, err = _require_auth(request)
    if err:
        return err

    db = get_db()
    user = db["users"].find_one({"username": payload["username"]}, {"_id": 0, "password": 0})

    if not user:
        return JsonResponse({"error": "User not found."}, status=404)

    return JsonResponse({"user": user})


# ---------------------------------------------------------------------------
# 7. Update Profile
# ---------------------------------------------------------------------------

@csrf_exempt
def update_profile(request):
    """PUT /userAuth/profile/update/  — requires Authorization: Bearer <token>"""
    if request.method != "PUT":
        return JsonResponse({"error": "Only PUT method is allowed."}, status=405)

    payload, err = _require_auth(request)
    if err:
        return err

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON body."}, status=400)

    allowed_fields = {"username", "email"}
    updates = {k: v for k, v in data.items() if k in allowed_fields and v}

    if not updates:
        return JsonResponse({"error": "No valid fields provided to update."}, status=400)

    db = get_db()

    if "username" in updates and updates["username"] != payload["username"]:
        if db["users"].find_one({"username": updates["username"]}):
            return JsonResponse({"error": "Username already taken."}, status=409)

    if "email" in updates:
        updates["email"] = updates["email"].strip().lower()
        if db["users"].find_one({"email": updates["email"]}):
            return JsonResponse({"error": "Email already in use."}, status=409)

    db["users"].update_one({"username": payload["username"]}, {"$set": updates})

    return JsonResponse({"message": "Profile updated successfully.", "updated_fields": updates})


# ---------------------------------------------------------------------------
# 8. Change Password
# ---------------------------------------------------------------------------

@csrf_exempt
def change_password(request):
    """PUT /userAuth/change-password/  — requires Authorization: Bearer <token>"""
    if request.method != "PUT":
        return JsonResponse({"error": "Only PUT method is allowed."}, status=405)

    payload, err = _require_auth(request)
    if err:
        return err

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON body."}, status=400)

    old_password = data.get("old_password", "")
    new_password = data.get("new_password", "")

    if not old_password or not new_password:
        return JsonResponse({"error": "old_password and new_password are required."}, status=400)

    db = get_db()
    user = db["users"].find_one({"username": payload["username"]})

    if not user:
        return JsonResponse({"error": "User not found."}, status=404)

    stored_pw = user["password"]
    if stored_pw.startswith("$2b$") or stored_pw.startswith("$2a$"):
        match = bcrypt.checkpw(old_password.encode(), stored_pw.encode())
    else:
        match = (old_password == stored_pw)

    if not match:
        return JsonResponse({"error": "Old password is incorrect."}, status=401)

    new_hashed = bcrypt.hashpw(new_password.encode(), bcrypt.gensalt()).decode()
    db["users"].update_one({"username": payload["username"]}, {"$set": {"password": new_hashed}})

    return JsonResponse({"message": "Password changed successfully."})