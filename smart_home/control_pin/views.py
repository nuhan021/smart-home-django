from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from .models import Pin
from .serializers import PinSerializer

class MyPin(APIView):
    def post(self, request):
        email = request.data.get("email")
        
        pin = Pin.objects.filter(email=email).first()

        serializer = PinSerializer(pin)
        return Response({"messege": serializer.data} , status=status.HTTP_200_OK)
        