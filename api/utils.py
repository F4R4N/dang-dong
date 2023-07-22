import secrets


def generate_slug():
    return secrets.token_urlsafe(16)