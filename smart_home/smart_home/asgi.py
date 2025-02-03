import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
import control_pin.routing



os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smart_home.settings')

application = get_asgi_application()


application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": URLRouter(control_pin.routing.websocket_urlpatterns,),
})



