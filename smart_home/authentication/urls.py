from django.urls import path
from .views import *


urlpatterns = [
    path('auth/register/', Registration_send_OTP.as_view(), name='register'),
    path('auth/verify-otp/', Registration_verify_OTP.as_view(), name= 'verify-otp'),
    path('auth/login/', Email_Authentication.as_view(), name='token_obtain'),
    path('auth/forgot-password/', Forgot_password.as_view(), name="forgot password"),
    path('auth/reset-password/', Reset_password.as_view(), name= "Reset password"),

    path('token/', Access_token.as_view(), name="access token"),

    path('user/', Auth_user.as_view(), name= "user"),

    path('local-ip/', Update_local_ip.as_view(), name="Update local ip"),
    path('add-device/', Add_device.as_view(), name='add new device'),

    path('edit-pin-details/', Edit_pin_details.as_view(), name='Edit-details'),

    path('add-room-switch/', Add_room_switch.as_view(), name='add room switch'),
    path('remove-room-switch/', Remove_room_switch.as_view(), name='remove room switch'),

    path('set-time/', Set_time_for_pin.as_view(), name='Set time'),
    
]
