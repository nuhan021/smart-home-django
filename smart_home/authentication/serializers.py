from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import serializers
from .models import User, PendingUser
from django.contrib.auth.password_validation import validate_password

# user model serializer
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'password', 'name', 'api_key']
        extra_kwargs = {
            'password': {'write_only': True},
            # 'api_key': {'write_only': True},
            }

    def validate_password(self, value):
        try:
            validate_password(value)
        except serializers.ValidationError as e:
            raise serializers.ValidationError({"password": e.messages})
        return value

    def create(self, validated_data):
        user = User.objects.create(**validated_data)
        user.set_password(validated_data["password"])
        user.is_staff = False
        user.is_superuser = False
        user.save()
        return user
    

# email token seriali
class EmailTokenObtainSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        user = User.objects.filter(email=email).first()

        if not user:
            raise serializers.ValidationError({"email":["User with this email does not exist"]})
        if not user.check_password(password):
            raise serializers.ValidationError({"password": ["Incorrect password."]})

        
        refresh = RefreshToken.for_user(user)
        return {
                'id': str(user.id),
                'email': str(user.email),
                'name': str(user.name),
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'created_at': str(user.created_at),
                'token_type': "Bearer",
                "expires_in": 1400 
            }
    

