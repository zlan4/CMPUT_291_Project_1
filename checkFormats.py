"""Checks if the format is correct."""
import re

def is_valid_email(email):
    """Checks if the email format is valid."""
    pattern = r'^[a-z0-9_]+@[a-z]+\.[a-zA-Z]{2,}$'
    if re.match(pattern, email):
        return True
    else:
        return False