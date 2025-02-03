from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.utils.timezone import now, timedelta
from django.contrib.auth.hashers import make_password
from django.utils.timezone import now, timedelta
import uuid


# user data base model
class UserManager(BaseUserManager):
    def create_user(self, email, password=None,name=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        user = self.model(email=email,name=name, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)
    

    

#user data abstract model
class User(AbstractBaseUser):
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=255)
    api_key = models.CharField(max_length=300, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']

    def clean(self):
        # Custom validation for name
        if not self.name:
            raise ValidationError(_('The Name field must be set'))
        if len(self.name) < 2:
            raise ValidationError(_('The Name field must have at least 2 characters'))
        

    

    def update_password(self, email, new_password):
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise ValueError("User with this email does not exist")
        user.set_password(new_password)
        user.save()
        return user

    def __str__(self):
        return self.email
    

# temp store user data while registering user


class PendingUser(models.Model):
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=255)
    password = models.CharField(max_length=255)  # Store hashed password
    otp = models.CharField(max_length=6)
    otp_created_at = models.DateTimeField(auto_now_add=True)  # Track OTP creation time
    created_at = models.DateTimeField(auto_now_add=True)      # Track record creation time

    def __str__(self):
        return self.email

    def is_otp_expired(self):
        expiry_duration = timedelta(minutes=5)  # OTP validity
        return now() > self.otp_created_at + expiry_duration

class PendingForgotPasswordUser(models.Model):
    email = models.EmailField(unique=True)
    otp = models.CharField(max_length=255)
    otp_created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email
    
    def is_otp_expired(self):
        expiry_duration = timedelta(minutes=5)  # OTP validity
        return now() > self.otp_created_at + expiry_duration