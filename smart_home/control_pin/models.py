from django.db import models

class Pin(models.Model):
    email = models.EmailField(unique=True, blank=False, null=False)
    active = models.BooleanField(default=False)

    # ON/OFF pins
    pin_1 = models.BooleanField(default=False)
    pin_2 = models.BooleanField(default=False)
    pin_3 = models.BooleanField(default=False)
    pin_4 = models.BooleanField(default=False)
    pin_5 = models.BooleanField(default=False)
    pin_6 = models.BooleanField(default=False)
    pin_7 = models.BooleanField(default=False)
    pin_8 = models.BooleanField(default=False)
    pin_9= models.BooleanField(default=False)
    pin_10 = models.BooleanField(default=False)
    pin_11 = models.BooleanField(default=False)
    pin_12 = models.BooleanField(default=False)
    pin_13 = models.BooleanField(default=False)
    pin_14 = models.BooleanField(default=False)
    pin_15 = models.BooleanField(default=False)


    #PWM values
    pwm_1 = models.IntegerField(default=0)
    pwm_2 = models.IntegerField(default=0)
    pwm_3 = models.IntegerField(default=0)
    pwm_4 = models.IntegerField(default=0)

    def __str__(self):
        return self.email
