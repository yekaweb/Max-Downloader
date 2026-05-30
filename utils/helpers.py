"""Helper utilities"""
import secrets
import string


def generate_referral_code(length: int = 10) -> str:
    """Generate unique referral code"""
    chars = string.ascii_uppercase + string.digits
    return "".join(secrets.choice(chars) for _ in range(length))


def truncate_string(text: str, max_length: int = 100) -> str:
    """Truncate string with ellipsis"""
    if len(text) > max_length:
        return text[:max_length] + "..."
    return text


__all__ = ["generate_referral_code", "truncate_string"]
