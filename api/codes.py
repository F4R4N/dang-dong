import secrets


def generate_id() -> str:
    """generates a url-safe token to use as id in models."""
    return secrets.token_urlsafe(16)


def generate_period_sharing_id() -> str:
    """generates a url-safe token to use as shareable link for periods."""
    return secrets.token_urlsafe(60)
