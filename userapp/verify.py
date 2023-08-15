import random
import os
from twilio.rest import Client

client = Client(os.environ["TWILIO_ACCOUNT_SID"], os.environ["TWILIO_AUTH_TOKEN"])
twilio_verify = client.verify.services(os.environ["TWILIO_VERIFY_SERVICE_SID"])

def generate_otp():
    return str(random.randint(100000, 999999))

def send_otp(phone, otp):
    twilio_verify.verifications.create(to=phone, channel="sms")

def check_otp(phone, code):
    try:
        result = twilio_verify.verification_checks.create(to=phone, code=code)
        return result.status == "approved"
    except Exception as e:
        return False