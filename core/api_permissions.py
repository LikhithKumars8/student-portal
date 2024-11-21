import datetime
from student.models import StudentPortalAdmin
from core.api_logger import api_logging
from core.encryption import jwt_decode_handler, crypto_decode
from jwt import DecodeError, ExpiredSignatureError
from django.core.exceptions import ObjectDoesNotExist

def has_permission(request):
    log_data = [f"info || {datetime.datetime.now()} auth function started"]
    try:
        # Extract 'authToken' from the Cookie header
        cookies = request.headers.get('Cookie')
        if not cookies:
            log_data.append("Error || Missing Cookie header")
            api_logging(log_data)
            return False

        # Parse the 'authToken' from the Cookie string
        auth_token = None
        for cookie in cookies.split(';'):
            key, value = cookie.strip().split('=', 1)
            if key == 'authToken':
                auth_token = value
                break

        if not auth_token:
            log_data.append("Error || Missing authToken in Cookie")
            api_logging(log_data)
            return False

        log_data.append(f"Debug || Extracted authToken: {auth_token[:15]}...")  # Mask token for logs

        try:
            # Decode the JWT token
            decoded_token = jwt_decode_handler(auth_token)
        except ExpiredSignatureError:
            log_data.append("Error || Token has expired")
            api_logging(log_data)
            return False
        except DecodeError:
            log_data.append("Error || Invalid token")
            api_logging(log_data)
            return False

        # Decode admin details from the token
        admin_id = crypto_decode(decoded_token.get('ai'))
        admin_email_id = crypto_decode(decoded_token.get('bi'))

        log_data.append(f"Debug || Decoded admin_id: {admin_id}, admin_email_id: {admin_email_id}")

        # Validate admin user in the database
        try:
            admin = StudentPortalAdmin.objects.get(
                id=int(admin_id),
                email=admin_email_id,
                is_active=True
            )
            log_data.append(f"Success || Admin validated: {admin.email}")
        except ObjectDoesNotExist:
            log_data.append("Error || Admin not found or inactive")
            api_logging(log_data)
            return False

        # Attach admin user to the request
        request.user = admin
        api_logging(log_data)
        return True

    except Exception as e:
        log_data.append(f"Error || Unexpected exception: {str(e)}")
        api_logging(log_data)
        return False
