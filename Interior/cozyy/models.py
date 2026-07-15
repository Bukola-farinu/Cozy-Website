from django.db import models

# Create your models here.
import uuid, random
from django.utils import timezone
from datetime import timedelta
from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    email_verified = models.BooleanField(default=False)
    otp_code = models.CharField(max_length=6, blank=True, null=True)
    otp_created_at = models.DateTimeField(blank=True, null=True)

    def generate_otp(self):
        self.otp_code = str(random.randint(100000, 999999))
        self.otp_created_at = timezone.now()
        self.save()
        return self.otp_code

    def otp_is_valid(self, code):
        if not self.otp_code or not self.otp_created_at:
            return False
        expired = timezone.now() > self.otp_created_at + timedelta(minutes=10)
        return (self.otp_code == code) and not expired
    
    def __str__(self):
        return self.user.username


class Inquiry(models.Model):
    PROJECT_TYPE_CHOICES = [
        ("living-room", "Living Room Renovation"),
        ("kitchen", "Bespoke Kitchen Upgrade"),
        ("outdoors", "Outdoor Living / Patio Space"),
        ("full-home", "Complete Structural Interior Design"),
    ]

    name = models.CharField(max_length=100)
    email = models.EmailField()
    project_type = models.CharField(max_length=20, choices=PROJECT_TYPE_CHOICES)
    message = models.TextField()
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.project_type}"