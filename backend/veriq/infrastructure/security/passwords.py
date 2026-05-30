from __future__ import annotations

from passlib.context import CryptContext

_password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Description: Hash a plaintext password using bcrypt.
    Parameters:
        password: Plaintext password.
    Returns:
        str: Secure password hash.
    Usage Example:
        hashed = hash_password("secret")
    """

    return _password_context.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    """Description: Verify a plaintext password against a hash.
    Parameters:
        password: Plaintext password.
        password_hash: Stored password hash.
    Returns:
        bool: True if the password matches the hash.
    Usage Example:
        is_valid = verify_password("secret", stored_hash)
    """

    return _password_context.verify(password, password_hash)
