"""
ASGI config for quizify project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/asgi/
"""

import os
from channels.auth import AuthMiddlewareStack
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter,URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
from quizroom import routing
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'quizify.settings')
django_asgi_app = get_asgi_application()
application = ProtocolTypeRouter(
    {
        "http":django_asgi_app,
        #Factory function which returns an OriginValidator configured to use settings.ALLOWED_HOSTS.
        "websocket":AllowedHostsOriginValidator(
            AuthMiddlewareStack(URLRouter(routing.websocket_urlpatterns))
        )
    }
)
