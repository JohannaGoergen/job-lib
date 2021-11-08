import logging

from django.conf import settings
from rest_framework.authentication import get_authorization_header
from rest_framework.exceptions import NotAuthenticated, PermissionDenied
from rest_framework.permissions import BasePermission

from google.auth.transport import requests as google_requests
from google.oauth2 import id_token


AUTH_SCHEME = "Bearer"

logger = logging.getLogger("authentication")


class IsAuthorizedPubSubRequest(BasePermission):
    def has_permission(self, request, view):
        try:
            auth = get_authorization_header(request)
            if not auth or auth.split()[0].lower() != AUTH_SCHEME.lower():
                raise NotAuthenticated("Missing authentication")
            token = auth[1].decode("utf-8")
            claim = id_token.verify_oauth2_token(
                token, google_requests.Request(), audience=settings.OIDC_TOKEN_AUDIENCE
            )
        except Exception as e:
            logger.warning(f"Invalid token sent to Pub/Sub subscriber: {e}")
            return False

        if claim["iss"] not in ["accounts.google.com", "https://accounts.google.com"]:
            raise PermissionDenied(f"Invalid claim")

        return True
