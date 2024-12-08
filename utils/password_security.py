import re

def check_password(password: str):
    """Checks if the password meets the required criteria."""
    if len(password) < 8:
        raise ValueError("Password must be at least 8 characters long.")
    if not re.search(r"\d", password):
        raise ValueError("Password must contain at least one digit.")
    if not re.search(r"[A-Za-z]", password):
        raise ValueError("Password must contain at least one letter.")
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        raise ValueError("Password must contain at least one special character.")
    return True
