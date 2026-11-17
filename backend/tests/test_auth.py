import uuid
from backend.app.core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    create_refresh_token,
    decode_token,
)

def test_password_hashing():
    raw = "SuperSecretPassword123!"
    hashed = get_password_hash(raw)
    assert hashed != raw
    assert verify_password(raw, hashed) is True
    assert verify_password("WrongPassword", hashed) is False

def test_jwt_token_encode_decode():
    user_id = uuid.uuid4()
    org_id = uuid.uuid4()
    role = "HR_ADMIN"

    access_token = create_access_token(user_id, org_id, role)
    decoded = decode_token(access_token)

    assert decoded is not None
    assert decoded["sub"] == str(user_id)
    assert decoded["org_id"] == str(org_id)
    assert decoded["role"] == role
    assert decoded["type"] == "access"

def test_refresh_token():
    user_id = uuid.uuid4()
    org_id = uuid.uuid4()
    refresh_token = create_refresh_token(user_id, org_id, "EMPLOYEE")
    decoded = decode_token(refresh_token)

    assert decoded is not None
    assert decoded["type"] == "refresh"
