
from django.contrib import admin
from django.urls import path, include
from authentication.views import Welcome


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('authentication.urls')),
    path('', Welcome.as_view(), name="Welcome"),


    # path('ws/', include('control_pin.routing'))
  
]
