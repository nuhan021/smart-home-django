from rest_framework.views import APIView
from .serializers import UserSerializer, EmailTokenObtainSerializer
from .models import PendingUser, User, PendingForgotPasswordUser
from control_pin.models import Pin
from .json_response import JsonResponse
import random
from .otp import OTP
from rest_framework_simplejwt.authentication import JWTTokenUserAuthentication
from rest_framework_simplejwt.tokens import RefreshToken
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.contrib.auth.password_validation import validate_password
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.hashers import make_password
import secrets
from django.core.validators import validate_ipv4_address




otp_obj = OTP()
user_object = User()

class Welcome(APIView):
    def get(self, request):
        return JsonResponse.success(
            code=200,
            message="You successfully make a GET request.",
            data= {}
        )

# take user info and send OTP to user Email
class Registration_send_OTP(APIView):
    def post(self, request):

    
        user_serializer = UserSerializer(data=request.data)

        if user_serializer.is_valid():

            # get email, name, password value from user_serializer
            email = user_serializer.validated_data['email']
            user_name = user_serializer.validated_data["name"]
            print(user_name)
            password = user_serializer.validated_data["password"]

            
            # check email already exist in PendingUser database
            if PendingUser.objects.filter(email=email,):
                # if email exist 
                return JsonResponse.error(
                    code=400,
                    message="Email already registered.Please check your mail or resend otp.",
                    errors={
                        "email": ["Email is already registered in Tempory database."],
                    }
                )

            
            #generate OPT
            generated_otp = random.randint(100000, 999999)

         
            # send OTP to user email
            user_otp = otp_obj.send_otp(email, generated_otp, user_name)

            if user_otp:
                # save the user temporarily in PendingUser database
                PendingUser.objects.create(
                    email=email,
                    name=user_name,
                    password=password,
                    otp=str(generated_otp)
                )
                return JsonResponse.success(
                    code=206,
                    message="OTP sent successfully. Please verify your email.",
                    data={
                        "email": email,
                        "expires_in": 300
                    }
                )

            
            # if OTP not send to user EMAIL
            return JsonResponse.error(
                code=500,
                message="Can not sent otp.",
                errors={
                    "email": [f"For an internal server problem, we can't sent your otp at {email}"]
                }
            )
            
        # if user_serializer not valid then return registration_failure
        messege = ''
        if user_serializer.errors.get('email'):
            messege = "Email: " + user_serializer.errors.get('email')[0]
        elif user_serializer.errors.get("password"):
            messege = "Password: " + user_serializer.errors.get("password")[0]
        elif user_serializer.errors.get("name"):
            messege = "Name: " + user_serializer.errors.get("name")[0]
        else:
            messege = "Registration failed."

        return JsonResponse.error(
            code=401,
            message=messege,
            errors= user_serializer.errors
        )
    


# verify OTP and Register new user to database
class Registration_verify_OTP(APIView):
    def post(self, request):

        # take email, otp form request
        email = request.data.get("email")
        otp = request.data.get("otp")

  
        
        # validating email that given email is correct format or not 
        try:
            validate_email(email)
        except ValidationError as e:
            return JsonResponse.error(
                code=400,
                message="Invalid email format.",
                errors=[
                    e.messages
                ]
            )



        # Check for pending user available or not
        try:
            pending_user = PendingUser.objects.get(email=email)
        except PendingUser.DoesNotExist:
            return JsonResponse.error(
                code=404,
                message="Invalid email.",
                errors={
                    "email": ["User not found or already verified."]
                }
            )
        
        # check OTP time validation, OTP expired or not?
        if pending_user.is_otp_expired():
            return JsonResponse.error(
                code=401,
                message="Otp time expired.Resend otp",
                errors={
                    "otp": ["OTP expired"]
                }
            )

        if pending_user.otp != otp:
            return JsonResponse.error(
                code=400,
                message="Invalid OTP.",
                errors={
                    "otp": ["Otp don't match.Ensure it is correct."]
                }
            )
        
        
        row_api_key = secrets.token_hex(32)
        # api_key = make_password(row_key)

        
        # Save user to main User database
        json_user_object = {
            "email": pending_user.email,
            "password": pending_user.password,
            "name": pending_user.name,
            "api_key": row_api_key
        }

        user_serializer = UserSerializer(data=json_user_object)

        if user_serializer.is_valid():
            user_serializer.save()
            Pin.objects.create(email=email)
            pending_user.delete()
            return JsonResponse.success(
                code=201,
                message="Registered successfully",
                data= user_serializer.data,
            )
            
        
        pending_user.delete()
        return JsonResponse.error(
            code=400,
            message="Registration failed",
            errors=user_serializer.errors
        )
            


# email authentication
class Email_Authentication(APIView):
    def post(self, request):
        serializer = EmailTokenObtainSerializer(data=request.data)
        if serializer.is_valid():
            return JsonResponse.success(
                code=200,
                message="Login successfyll",
                data=serializer.validated_data,
            )
        
        return JsonResponse.error(
            code=401,
            message="Login failed.Please make sure your email & password is correct.",
            errors=serializer.errors,
        )

    
# forgot password send  otp
class Forgot_password(APIView):

    def post(self, request):

        email = request.data.get("email")


       # validating email that given email is correct format or not 
        try:
            validate_email(email)
        except ValidationError as e:
            return JsonResponse.error(
                code=400,
                message="Invalid email format.",
                errors={
                    "email": e.messages
                }
            )


        
        # Check if email exist in User database
        if not User.objects.filter(email=email):
            return JsonResponse.error(
                code=401,
                message="User with this email not found",
                errors={
                    "email": ["No account found with the provided email address."]
                }
            )


        
        # Check if email exists in the PendingForgotPasswordUser
        if PendingForgotPasswordUser.objects.filter(email=email):
                return JsonResponse.error(
                    code=400,
                    message="Email is already used for reset password. Please check your email for an otp or resend otp",
                    errors={
                        "email": ["User already used this email for send otp."]
                    }
                )

        
        # Generate OPT for resetting password
        generated_otp = random.randint(100000, 999999)

        # send otp
        user_otp = otp_obj.send_otp(email=email, otp_type="forgotPassword", otp=generated_otp)
        
        # if user_otp return true
        if user_otp:
            PendingForgotPasswordUser.objects.create(email=email, otp=generated_otp)
            return JsonResponse.success(
                code=206,
                message="OTP sent successfully. Please check your email.",
                data={
                    "email": email,
                    "expires_in": 300
                }
            )
            
            
        # if OTP not send to user EMAIL
        return JsonResponse.error(
                code=500,
                message="Can not sent otp.",
                errors={
                    "otp": ["For an internal server problem, we can't sent your otp!"]
                }
        )


# reset forgotten password
class Reset_password(APIView):

    def post(self, request):

        email = request.data.get("email")
        otp = request.data.get("otp")
        new_password = request.data.get("password")


        #check email and otp provided correctly
        if not email and not otp and not new_password:
            return JsonResponse.error(
                code=400,
                message="Invalid email, otp & password",
                errors={
                    "email": ["Email field must be field"],
                    "otp": ["OTP field must be fild"],
                    "password": ["password field must be field"]
                }
            )
        
        try:
            validate_email(email)
        except ValidationError as e:
            return JsonResponse.error(
                code=400,
                message="Invalid email",
                errors={
                    "email": [e.messages]
                }
            )

        
        if not otp:
            return JsonResponse.error(
                code=400,
                message="Otp field must be field",
                errors={
                    "email": ["Otp field must be field",]
                }
            )
        
        
        try:
            validate_password(new_password)
        except ValidationError as e:
            return JsonResponse.error(
                code=400,
                message="Invalid password.Password must contain at least 8 character and use upprcase and lowercase",
                errors={
                    "email": e.messages
                }
            )
        
        
        # Check for pending user available or not
        try:
            pending_forgot_password_user = PendingForgotPasswordUser.objects.get(email=email)
        except PendingForgotPasswordUser.DoesNotExist:
            return JsonResponse.error(
                code=404,
                message="Invalid email",
                errors=[
                    "User not found or already verified with this email"
                ]
            )
        
        # check OTP time validation, OTP expired or not?
        if pending_forgot_password_user.is_otp_expired():
            return JsonResponse.error(
                code=401,
                message="Otp expired",
                errors=[
                    "OTP expired.Please register again."
                ]
            )

        if pending_forgot_password_user.otp != otp:
            return JsonResponse.error(
                code=400,
                message="Invalid OTP.",
                errors=[
                    "Otp not match.Please check your mail and give correct otp."
                ]
            )
        
        # if all goes perfect
        user_object.update_password(email=email, new_password=new_password)
        pending_forgot_password_user.delete()
   

        return JsonResponse.success(
            code=200,
            message="Password reset successfully",
            data= {
                "email": email
            }
        )
        
        
# create access and refresh token
class Access_token(APIView):

    def post(self, request):

        refresh_token = request.data.get("refresh")

        if not refresh_token:
            return JsonResponse.error(
                code=400,
                message="Empyty token or field.",
                errors={
                    "token": ["Refresh field must be include,it can not be empty."]
                }
            )
        
        try:
            decoded_token = RefreshToken(refresh_token)
        except Exception as e:
            
            return JsonResponse.error(
                code=400,
                message="Token not valid",
                errors={
                    "token": e.message,
                }
            )

        
        try:
            user = User.objects.get(id=decoded_token['user_id'])
        except User.DoesNotExist:
            return JsonResponse.error(
                code=401,
                message="Invalid token",
                errors={
                    "email": [ "Invalid authentication credentials."]
                }
            )
            
        
        refresh = RefreshToken.for_user(user)
        return JsonResponse.success(
            code=201,
            message="Access token",
            data={
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            }
        )


# # verify using access token before access user info
class Auth_user(APIView):
    authentication_classes = [JWTTokenUserAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if not request.user or not request.user.is_authenticated:
            return JsonResponse.error(
                code=401,
                message="Invalid token",
                errors={
                    "token": ["Authentication credentials were not provided or invalid."]
                }
            )

        
        id = request.user.id

        try:
            user = User.objects.get(id=id)
        except User.DoesNotExist:
            return JsonResponse.error(
                code=401,
                message="Invalid token",
                errors={
                    "token": ["Invalid authentication credentials."]
                }
            )


        
        email = user.email
        user_pins = Pin.objects.get(email=email)

        return JsonResponse.success(
            code=200,
            message="Authentication successful.",
            data={
                "user":{
                    'id': user.id,
                    'email': user.email,
                    'name': user.name,
                    'created_at': user.created_at,
                    'local_ip': user.local_ip,
                },
                "pins": {
                    "pin_1":user_pins.pin_1,
                    "pin_2":user_pins.pin_2,
                    "pin_3":user_pins.pin_3,
                    "pin_4":user_pins.pin_4,
                    "pin_5":user_pins.pin_5,
                    "pin_6":user_pins.pin_6,
                    "pin_7":user_pins.pin_7,
                    "pin_8":user_pins.pin_8,
                }
            }
        )


class Update_local_ip(APIView) :
    
    def post(self, request):
        api_key = request.query_params.get("api-key")
        local_ip = request.query_params.get("local-ip")
        try :
            user = User.objects.get(api_key = api_key)
        except User.DoesNotExist:
            return JsonResponse.error(
                code=401,
                message="No user found",
                errors={
                    "api-key": ["invalid api key"]
                }
            )
        

        try:
            validate_ipv4_address(local_ip)  
            user = User.objects.get(email=user.email)
        except User.DoesNotExist:
            return JsonResponse.error(
                code=401,
                message="No user found",
                errors={
                    "api-key": ["invalid Email"]
                }
            )
        except ValidationError:
            return JsonResponse.error(
                code=401,
                message="Invalid ip address format",
                errors={
                    "ip": ["invalid ip"]
                }
            )

        user.local_ip = local_ip
        user.save()
        return JsonResponse.success(
            code=200,
            message="Successfully updated",
            data= {
                "ip": user.local_ip
            }
        )
