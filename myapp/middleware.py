# myapp/middleware.py
from msal import ConfidentialClientApplication
from django.conf import settings
from django.http import JsonResponse
from functools import wraps

# Function to validate the token using MSAL
def validate_token(func):
    @wraps(func)
    def wrapper(request, *args, **kwargs):
        # Extract the token from the 'Authorization' header
        token = request.headers.get('Authorization')
        if not token:
            return JsonResponse({"error": "Authorization token missing"}, status=401)

        # Token should be in the format "Bearer <token>"
        token = token.split(' ')[1]  # Extract token after "Bearer "

        # Initialize MSAL ConfidentialClientApplication to validate the token
        app = ConfidentialClientApplication(
            settings.MSAL_CLIENT_ID,
            authority=settings.MSAL_AUTHORITY,
            client_credential=settings.MSAL_CLIENT_SECRET
        )

        # Attempt to validate the token by acquiring the on-behalf-of token
        result = app.acquire_token_on_behalf_of(token, scopes=["openid", "profile", "email"])
        
        if not result:
            return JsonResponse({"error": "Invalid token"}, status=401)

        # Proceed with the original view function if token is valid
        return func(request, *args, **kwargs)

    return wrapper
