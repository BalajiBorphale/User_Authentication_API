import random
import string
# from django.conf import settings # This import might not be strictly needed for these two functions, but doesn't hurt.

def generate_otp(length=6):
    return ''.join(random.choices(string.digits, k=length))

def send_mock_otp_email(email, otp_code):

    print(f"\n--- MOCK EMAIL SERVICE ---")
    print(f"To: {email}")
    print(f"Subject: Your OTP for Login")
    print(f"Body: Your One-Time Password is: {otp_code}")
    print(f"---------------------------\n")