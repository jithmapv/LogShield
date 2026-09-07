from app.models import UserRole
from app.security import create_access_token, hash_password, verify_password


def test_password_hash_and_jwt():
    password = "a-strong-test-password"
    assert verify_password(password, hash_password(password))
    token = create_access_token("alice", UserRole.analyst)
    assert isinstance(token, str) and token.count(".") == 2