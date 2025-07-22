from rest_framework import serializers
from .models import User, OTP
from django.utils import timezone

class UserRegistrationSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("This email is already registered.")
        return value

    def create(self, validated_data):
        return User.objects.create(email=validated_data['email'])

class OTPRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError("No user found with this email.")
        return value

class OTPVerificationSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=6)

    def validate(self, data):
        email = data.get('email')
        otp_code = data.get('otp')

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError("Invalid email or OTP.")

        # Find the latest valid OTP for the user that matches the provided code
        latest_otp = OTP.objects.filter(
            user=user,
            code=otp_code, # Filter by code directly
            is_used=False,
            expires_at__gt=timezone.now()
        ).order_by('-created_at').first()

        if not latest_otp:
            raise serializers.ValidationError("Invalid or expired OTP.")

        data['user'] = user # Attach user object for view to use
        data['otp_instance'] = latest_otp # Attach OTP instance for view to use
        return data
