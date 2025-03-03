from rest_framework.views import exception_handler
from rest_framework.exceptions import AuthenticationFailed, NotAuthenticated
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from django.http import JsonResponse

def custom_exception_handler(exc, context):
    
    response = exception_handler(exc, context)

    
    if isinstance(exc, (AuthenticationFailed, NotAuthenticated, InvalidToken, TokenError)):
        return JsonResponse({
            "status": "error",
            "code": 401,
            "message": "Invalid or expired token",
            "errors": {
                "token":["Authentication credentials were not provided or invalid."]
            }
        }, status=401)

    return response