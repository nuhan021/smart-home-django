from django.db import models

class Pin(models.Model):
    email = models.EmailField(unique=True, blank=False, null=False)
    pin_1 = models.BooleanField(default=False)
    pin_2 = models.BooleanField(default=False)
    pin_3 = models.BooleanField(default=False)
    pin_4 = models.BooleanField(default=False)
    pin_5 = models.BooleanField(default=False)
    pin_6 = models.BooleanField(default=False)
    pin_7 = models.BooleanField(default=False)
    pin_8 = models.BooleanField(default=False)

    def __str__(self):
        return self.email
