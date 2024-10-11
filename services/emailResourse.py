import secrets
from datetime import datetime, timedelta, timezone

# Generar token
def generate_token():
    token = secrets.token_urlsafe(5)
    expiration = datetime.now(timezone.utc) + timedelta(hours=1)
    return token, expiration
