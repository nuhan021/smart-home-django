from apscheduler.schedulers.background import BackgroundScheduler
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.utils.timezone import now
from .models import Pin
from authentication.models import User
import datetime

def check_pin_times():
    now_time = now().time()
    current_hour = now_time.hour
    current_minute = now_time.minute

    pins = Pin.objects.all()

    for pin in pins:
        for i in range(1, 17):
            pin_key = f"pin_{i}"
            on_time_field = f"{pin_key}_on_time"
            off_time_field = f"{pin_key}_off_time"

            on_time = getattr(pin, on_time_field, None)
            off_time = getattr(pin, off_time_field, None)

            if on_time and on_time.hour == current_hour and on_time.minute == current_minute:
                print(f"ON Triggered for {pin_key} at {current_hour}:{current_minute}")
                send_ws_message(pin.email, pin_key, True)

            if off_time and off_time.hour == current_hour and off_time.minute == current_minute:
                print(f"OFF Triggered for {pin_key} at {current_hour}:{current_minute}")
                send_ws_message(pin.email, pin_key, False)

def send_ws_message(email, pin_key, action):
    try:
        user = User.objects.get(email=email)
        pin = Pin.objects.get(email=email)
        group_name = user.api_key + str(user.id)
        channel_layer = get_channel_layer()

        setattr(pin, pin_key, action)
        pin.save()
        async_to_sync(channel_layer.group_send)(
            group_name,
            {
                "type": "send_message",
                "message": {
                    "status": "success",
                    "code": 200,
                    "message": f"{pin_key} turned {action}",
                    "data": {
                       "pins": [
                           {pin_key: action}
                       ]
                    }
                }
            }
        )
    except Exception as e:
        print(f"WebSocket send failed: {e}")

def start_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(check_pin_times, "interval", seconds=10)
    print("✅ Scheduler started!")
    scheduler.start()
