from django.urls import path
from .views import UserRegistrationView, RequestOTPView, VerifyOTPView

urlpatterns = [
    path('register', UserRegistrationView.as_view(), name='register'),
    path('request-otp', RequestOTPView.as_view(), name='request-otp'),
    path('verify-otp', VerifyOTPView.as_view(), name='verify-otp'),
]
