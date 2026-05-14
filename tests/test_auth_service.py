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

    def test_password_too_short(self, engine):
        with pytest.raises(ValueError, match="8 Zeichen"):
            _make(engine).register("Roy", "F", "roy@test.ch", "Ab1!")

    def test_password_no_special_char(self, engine):
        with pytest.raises(ValueError, match="Sonderzeichen"):
            _make(engine).register("Roy", "F", "roy@test.ch", "Password123")

    def test_invalid_email(self, engine):
        with pytest.raises(ValueError, match="E-Mail"):
            _make(engine).register("Roy", "F", "not-an-email", "Secret123!")

    def test_invalid_phone(self, engine):
        with pytest.raises(ValueError, match="Telefonnummer"):
            _make(engine).register("Roy", "F", "roy@test.ch", "Secret123!", phone="abc")

    def test_duplicate_email(self, engine):
        auth = _make(engine)
        auth.register("Roy", "F", "roy@test.ch", "Secret123!")
        with pytest.raises(ValueError, match="existiert bereits"):
            auth.register("Roy", "F", "roy@test.ch", "Secret123!")
