from django.contrib import admin
from  .models import User, PendingUser, PendingForgotPasswordUser

admin.site.register(User)
admin.site.register(PendingUser)
admin.site.register(PendingForgotPasswordUser)
