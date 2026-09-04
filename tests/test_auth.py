"""
tests/test_auth.py - Unit Tests for Authentication and Password Hashing
"""

import os
import tempfile
import pytest
from database import db
from auth.auth import hash_password, verify_password, register_user, authenticate_user


@pytest.fixture
def temp_db():
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    db.init_db(db_path=path)
    yield path
    if os.path.exists(path):
        os.remove(path)


def test_password_hashing():
    pw = "SecurePass123!"
    hashed = hash_password(pw)
    assert hashed != pw
    assert verify_password(pw, hashed) is True
    assert verify_password("WrongPass123!", hashed) is False


def test_register_and_authenticate(temp_db):
    ok, msg, uid = register_user("fitfan", "fan@fitcoach.ai", "Secret1234", "Secret1234", "Fit Fan", db_path=temp_db)
    assert ok is True
    assert uid is not None

    # Duplicate username
    ok, msg, _ = register_user("fitfan", "other@fitcoach.ai", "Secret1234", "Secret1234", db_path=temp_db)
    assert ok is False

    # Duplicate email
    ok, msg, _ = register_user("otheruser", "fan@fitcoach.ai", "Secret1234", "Secret1234", db_path=temp_db)
    assert ok is False

    # Mismatched passwords
    ok, msg, _ = register_user("newuser", "new@fitcoach.ai", "Secret1234", "Different1234", db_path=temp_db)
    assert ok is False

    # Short password (< 6 chars)
    ok, msg, _ = register_user("newuser2", "new2@fitcoach.ai", "123", "123", db_path=temp_db)
    assert ok is False

    # Authenticate with username
    ok, msg, user = authenticate_user("fitfan", "Secret1234", db_path=temp_db)
    assert ok is True
    assert user["username"] == "fitfan"

    # Authenticate with email
    ok, msg, user = authenticate_user("fan@fitcoach.ai", "Secret1234", db_path=temp_db)
    assert ok is True
    assert user["username"] == "fitfan"

    # Authenticate with wrong password
    ok, msg, user = authenticate_user("fitfan", "WrongPassword", db_path=temp_db)
    assert ok is False
    assert user is None
