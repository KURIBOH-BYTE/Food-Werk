import pytest
from foodwerk.data_access.dao import DeliveryAddressDAO, UserDAO
from foodwerk.services.auth_service import AuthService


def _make(engine) -> AuthService:
    return AuthService(user_dao=UserDAO(engine), address_dao=DeliveryAddressDAO(engine))


class TestAuthService:
    def test_register_creates_user(self, engine):
        user = _make(engine).register("Roy", "Fluckiger", "roy@test.ch", "Secret123!")
        assert user.id is not None
        assert user.first_name == "Roy"
        assert user.email == "roy@test.ch"
        assert user.role == "customer"

    def test_login_success(self, engine):
        auth = _make(engine)
        auth.register("Roy", "Fluckiger", "roy@test.ch", "Secret123!")
        user = auth.login("roy@test.ch", "Secret123!")
        assert user is not None
        assert user.email == "roy@test.ch"

    def test_login_wrong_password(self, engine):
        auth = _make(engine)
        auth.register("Roy", "Fluckiger", "roy@test.ch", "Secret123!")
        assert auth.login("roy@test.ch", "wrongpassword") is None
