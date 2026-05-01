"""Authentication service — registration, login, password hashing."""

from __future__ import annotations

from typing import Optional

import bcrypt

from .base_service import BaseService
from ..data_access.dao import UserDAO
from ..domain.models import User


class AuthService(BaseService):

    def __init__(self, user_dao: UserDAO) -> None:
        self.user_dao = user_dao

    def get_by_id(self, entity_id: int) -> Optional[User]:
        return self.user_dao.get_by_id(entity_id)

    def get_all(self) -> list[User]:
        return self.user_dao.get_all()

    # ------------------------------------------------------------------

    def hash_password(self, password: str) -> str:
        return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    def verify_password(self, password: str, password_hash: str) -> bool:
        return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))

    def register(
        self,
        first_name: str,
        last_name: str,
        email: str,
        password: str,
        phone: Optional[str] = None,
    ) -> User:
        if not all([first_name, last_name, email, password]):
            raise ValueError("All required fields must be filled in.")
        if self.user_dao.get_by_email(email):
            raise ValueError("An account with this email already exists.")

        user = User(
            first_name=first_name,
            last_name=last_name,
            email=email,
            password_hash=self.hash_password(password),
            phone=phone,
            role="customer",
        )
        return self.user_dao.create(user)

    def login(self, email: str, password: str) -> Optional[User]:
        user = self.user_dao.get_by_email(email)
        if user and self.verify_password(password, user.password_hash):
            return user
        return None
