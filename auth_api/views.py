from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView

from django.db import transaction
from django.conf import settings
from django.core.cache import cache # Used for rate limiting
from django.utils import timezone
import jwt # For manual JWT generation
from datetime import timedelta # For JWT expiration

from .models import User, OTP
from .serializers import UserRegistrationSerializer, OTPRequestSerializer, OTPVerificationSerializer
from .utils import generate_otp, send_mock_otp_email

class UserRegistrationView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(
            {"message": "Registration successful. Please request an OTP to log in."},
            status=status.HTTP_201_CREATED
        )

class RequestOTPView(APIView):
    serializer_class = OTPRequestSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"error": "No user found with this email."}, status=status.HTTP_404_NOT_FOUND)

        # Basic Rate Limiting (using Django's cache)
        cache_key = f"otp_request_limit_{email}"
        request_count = cache.get(cache_key, 0)

        if request_count >= settings.OTP_RATE_LIMIT_COUNT:
            return Response(
                {"error": f"Too many OTP requests. Please wait {settings.OTP_RATE_LIMIT_SECONDS} seconds before trying again."},
                status=status.HTTP_429_TOO_MANY_REQUESTS
            )

        with transaction.atomic():
            # Invalidate any previous unused OTPs for this user to ensure only the latest is valid
            OTP.objects.filter(user=user, is_used=False, expires_at__gt=timezone.now()).update(is_used=True)

            otp_code = generate_otp()
            OTP.objects.create(user=user, code=otp_code)

            send_mock_otp_email(email, otp_code)

            # Increment request count and set/reset cache expiry
            # If cache_key doesn't exist, it sets it. If it does, it increments and extends expiry.
            cache.set(cache_key, request_count + 1, timeout=settings.OTP_RATE_LIMIT_SECONDS)

        return Response({"message": "OTP sent to your email."}, status=status.HTTP_200_OK)


class VerifyOTPView(APIView):
    serializer_class = OTPVerificationSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data['user']
        otp_instance = serializer.validated_data['otp_instance']

        with transaction.atomic():
            # Mark OTP as used
            otp_instance.is_used = True
            otp_instance.save()

            # Mark user as verified if it's their first successful login
            if not user.is_verified:
                user.is_verified = True
                user.save()

            # Generate JWT token
            access_token_payload = {
                'user_id': user.id,
                'exp': timezone.now() + timedelta(minutes=60), # Token valid for 60 mins
                'iat': timezone.now(),
                'email': user.email # Include email in token payload
            }
            token = jwt.encode(access_token_payload, settings.SECRET_KEY, algorithm="HS256")

        return Response({
            "message": "Login successful.",
            "token": token
        }, status=status.HTTP_200_OK)
