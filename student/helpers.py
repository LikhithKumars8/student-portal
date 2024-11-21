from student.models import StudentPortalAdmin

def admin_verification(password, name):
    """
    Verifies the OTP (one-time password) for a user based on the provided mobile number and OTP.
    """
    try:
        # Admin info and verify
        user_obj = StudentPortalAdmin.objects.filter(password=password, name=name ,is_active=True).first()
        # Verify the otp
        return user_obj if user_obj else None
    except Exception:
        return None