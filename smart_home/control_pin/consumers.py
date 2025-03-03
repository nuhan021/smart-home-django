import json
from channels.generic.websocket import AsyncWebsocketConsumer
from urllib.parse import parse_qs
from rest_framework_simplejwt.tokens import AccessToken
from authentication.models import User
from asgiref.sync import sync_to_async
from .models import Pin
import asyncio


class MyConsumer(AsyncWebsocketConsumer):

    group_name = "group"
    user = None
    pin = None


    async def connect(self):
        query_string = parse_qs(self.scope["query_string"].decode())
        api_key = query_string.get("api-key", [None])[0]
        self.keep_alive_task = None

        try:
            self.user = await sync_to_async(User.objects.get)(api_key=api_key)
            self.pin = await sync_to_async(Pin.objects.get)(email = self.user.email)
            self.group_name = self.user.name + str(self.user.id)

            await self.channel_layer.group_add(
                self.group_name,
                self.channel_name,
            )

            await self.accept()

            await self.channel_layer.group_send(
                    self.group_name,
                    {"type": "send_message", 
                     "message": self.success(message="Sent succesfull", data=
                    {
                        "pins" : [
                                    {"pin_1": self.pin.pin_1},
                                    {"pin_2": self.pin.pin_2},
                                    {"pin_3": self.pin.pin_3},
                                    {"pin_4": self.pin.pin_4},
                                    {"pin_5": self.pin.pin_5},
                                    {"pin_6": self.pin.pin_6},
                                    {"pin_7": self.pin.pin_7},
                                    {"pin_8": self.pin.pin_8},
                                    {"pin_9": self.pin.pin_9},
                                    {"pin_10": self.pin.pin_10},
                                    {"pin_11": self.pin.pin_11},
                                    {"pin_12": self.pin.pin_12},
                                    {"pin_13": self.pin.pin_13},
                                    {"pin_14": self.pin.pin_14},
                                    {"pin_15": self.pin.pin_15},
                                ],
                        "pwms": [
                            {"pwm_1": self.pin.pwm_1},
                            {"pwm_2": self.pin.pwm_2},
                            {"pwm_3": self.pin.pwm_3},
                            {"pwm_4": self.pin.pwm_4},
                        ]
                    })}
            )

            # Start Keep-Alive Mechanism
            self.keep_alive_task = asyncio.create_task(self.keep_alive())




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

        # Stop Keep-Alive Task
        if self.keep_alive_task is not None:
            self.keep_alive_task.cancel()




    async def receive(self, text_data):
        try:
            data = json.loads(text_data)

             # Handle "pong" messages from ESP32
            if data.get("type") == "pong":
                print("Received Pong from ESP32")
                return  

            # print(f"Received: {data}")

            filtered_pin_data = [
                {key: value} for key, value in data.items() if key.startswith("pin_")
            ]

            filtered_pwm_data = [
                {key: value} for key, value in data.items() if key.startswith("pwm_")
            ]
            

            if filtered_pin_data:
                for item in filtered_pin_data:
                    for key, value in item.items():
                        if hasattr(self.pin, key):
                            setattr(self.pin, key, value)

                await sync_to_async(self.pin.save)()
                            


                await self.channel_layer.group_send(
                    self.group_name,
                    {"type": "send_message", "message": self.success(message="Update succesfull", data={
                        "pins": filtered_pin_data
                    })}
                )

            if filtered_pwm_data:
                for item in filtered_pwm_data:
                    for key, value in item.items():
                        if hasattr(self.pin, key):
                            setattr(self.pin, key, value)

                await sync_to_async(self.pin.save)()
                            


                await self.channel_layer.group_send(
                    self.group_name,
                    {"type": "send_message", "message": self.success(message="Update succesfull", data={
                        "pwms": filtered_pwm_data
                    })}
                )
        
        except json.JSONDecodeError:
            # print("Invalid JSON format received!")
            # await self.send(text_data=json.dumps({"error": "Invalid JSON format!"}))
            await self.send(text_data=json.dumps(self.error(400, "Invalid json format")))

        
         

    async def keep_alive(self):
        while True:
            await asyncio.sleep(25)
            try:
                await self.send(text_data=json.dumps({"type": "ping"}))
                print("Server Sent Ping")

                
            except Exception as e:
                print(f"Ping Error: {e}")
                break
        

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

    