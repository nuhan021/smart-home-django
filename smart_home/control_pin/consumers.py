import json
from channels.generic.websocket import AsyncWebsocketConsumer
from urllib.parse import parse_qs
from rest_framework_simplejwt.tokens import AccessToken
from authentication.models import User
from asgiref.sync import sync_to_async
from .models import Pin
from .serializers import PinSerializer

class MyConsumer(AsyncWebsocketConsumer):

    group_name = "group"
    user = None
    pin = None


    async def connect(self):
        query_string = parse_qs(self.scope["query_string"].decode())
        api_key = query_string.get("api-key", [None])[0]

        try:
            self.user = await sync_to_async(User.objects.get)(api_key=api_key)
            self.group_name = self.user.name + str(self.user.id)
            self.pin = await sync_to_async(Pin.objects.get)(email = self.user.email)


            await self.channel_layer.group_add(
                self.group_name,
                self.channel_name,
            )

            await self.accept()
            # print("Websocket connect")
            print(f"Group name: {self.group_name}")
        except User.DoesNotExist:
            # print("Not authenticated")
            await self.close()




    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.group_name, 
            self.channel_name
        )

        # print("Websocket disconnected!")




    async def receive(self, text_data):
        try:
            data = json.loads(text_data)

            # print(f"Received: {data}")

            filtered_data = {key: value for key, value in data.items() if key.startswith("pin_")}

            if filtered_data:
                for key, value in filtered_data.items():
                    if key.startswith("pin_"):
                        if hasattr(self.pin, key):
                            setattr(self.pin, key, value)

                await sync_to_async(self.pin.save)()

                # pin_serializer = PinSerializer(self.pin)
                            


                await self.channel_layer.group_send(
                    self.group_name,
                    {"type": "send_message", "message": self.success(message="Update succesfull", data=filtered_data)}
                )
        
        except json.JSONDecodeError:
            # print("Invalid JSON format received!")
            # await self.send(text_data=json.dumps({"error": "Invalid JSON format!"}))
            await self.send(text_data=json.dumps(self.error(400, "Invalid json format")))

        
        

    async def send_message(self, event):
        await self.send(text_data=json.dumps({"message": event["message"]}))


    def success(self, code=200, message="Request was successful.", data=None):
        return {
            "status": "success",
            "code": code,
            "message": message,
            "data": data or {}
        }

    def error(self,code, message):
        return {
            "status": "error",
            "code": code,
            "message": message,
        }

    