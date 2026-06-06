from django.conf import settings
from django.http import HttpResponse


class SimpleCorsMiddleware:
    """Add CORS headers for configured origins and handle preflight requests."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        origin = request.headers.get("Origin")
        allow_all_origins = getattr(settings, "CORS_ALLOW_ALL_ORIGINS", False)
        allowed_origins = {
            configured_origin.rstrip("/")
            for configured_origin in getattr(settings, "CORS_ALLOWED_ORIGINS", [])
        }
        origin_normalized = origin.rstrip("/") if origin else None

        if request.method == "OPTIONS":
            response = HttpResponse(status=204)
        else:
            response = self.get_response(request)

        if allow_all_origins:
            response["Access-Control-Allow-Origin"] = origin if origin else "*"
            response["Vary"] = "Origin"
            response["Access-Control-Allow-Methods"] = "GET, POST, PUT, PATCH, DELETE, OPTIONS"
            response["Access-Control-Allow-Headers"] = "Authorization, Content-Type"
            response["Access-Control-Allow-Credentials"] = "true"
        elif origin_normalized and origin_normalized in allowed_origins:
            response["Access-Control-Allow-Origin"] = origin
            response["Vary"] = "Origin"
            response["Access-Control-Allow-Methods"] = "GET, POST, PUT, PATCH, DELETE, OPTIONS"
            response["Access-Control-Allow-Headers"] = "Authorization, Content-Type"
            response["Access-Control-Allow-Credentials"] = "true"

        return response