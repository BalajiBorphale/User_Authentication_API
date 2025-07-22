from django.db import models
from django.conf import settings
from django.utils import timezone
import datetime

class User(models.Model):
    email = models.EmailField(unique=True)
    is_active = models.BooleanField(default=True)
    is_verified = models.BooleanField(default=False) # True after first successful OTP login

    def __str__(self):
        return self.email

class OTP(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if not self.id: # Only set expiry for new objects
            self.expires_at = timezone.now() + datetime.timedelta(minutes=settings.OTP_EXPIRY_MINUTES)
        super().save(*args, **kwargs)

    def is_valid(self):
        return not self.is_used and self.expires_at > timezone.now()

    def __str__(self):
        return f"{self.user.email} - {self.code}"
