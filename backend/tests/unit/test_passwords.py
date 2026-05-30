from __future__ import annotations

from veriq.infrastructure.security.passwords import hash_password, verify_password


def test_password_hashing() -> None:
    """Description: Validate password hashing and verification.
    Parameters:
        None
    Returns:
        None
    Usage Example:
        test_password_hashing()
    """

    hashed = hash_password("secret")
    assert verify_password("secret", hashed)
    assert not verify_password("wrong", hashed)
