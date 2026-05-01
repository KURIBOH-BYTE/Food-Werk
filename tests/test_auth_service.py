from foodwerk.data_access.dao import UserDAO
from foodwerk.services.auth_service import AuthService


class TestAuthService:
    def test_register_creates_user(self, engine):
        auth = AuthService(user_dao=UserDAO(engine))
        user = auth.register("Roy", "Fluckiger", "roy@test.ch", "password123")
        assert user.id is not None
        assert user.first_name == "Roy"
        assert user.email == "roy@test.ch"
        assert user.role == "customer"

    def test_login_success(self, engine):
        auth = AuthService(user_dao=UserDAO(engine))
        auth.register("Roy", "Fluckiger", "roy@test.ch", "password123")
        user = auth.login("roy@test.ch", "password123")
        assert user is not None
        assert user.email == "roy@test.ch"
