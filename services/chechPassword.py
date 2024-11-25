import re

def check_password(password):
    min_length = 8

    if len(password) < min_length:
        return f"Password must be at least {min_length} characters long"

    if not any(char.islower() for char in password):
        return "Lowercase letter missing"

    if not any(char.isupper() for char in password):
        return "Uppercase letter missing"

    if not any(char.isdigit() for char in password):
        return "No number"

