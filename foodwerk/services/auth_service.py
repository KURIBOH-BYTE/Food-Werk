"""Authentication service — registration, login, password hashing."""

from __future__ import annotations

import re
from typing import Optional

import bcrypt

from .base_service import BaseService
from ..data_access.dao import DeliveryAddressDAO, UserDAO
from ..domain.models import DeliveryAddress, User

_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
_PHONE_RE = re.compile(r"^\+?[\d\s\-\(\)]{7,20}$")
_SPECIAL_RE = re.compile(r"[!@#$%^&*()_+\-=\[\]{};':\"\\|,.<>\/?`~]")
_NAME_RE = re.compile(r"^[A-Za-zÀ-öø-ÿ\s\-']+$")


class AuthService(BaseService):

    def __init__(self, user_dao: UserDAO, address_dao: DeliveryAddressDAO) -> None:
        self.user_dao = user_dao
        self.address_dao = address_dao

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
        errors: list[str] = []

        if not first_name.strip():
            errors.append("Vorname ist ein Pflichtfeld.")
        elif not _NAME_RE.match(first_name.strip()):
            errors.append("Vorname darf keine Sonderzeichen enthalten.")
        if not last_name.strip():
            errors.append("Nachname ist ein Pflichtfeld.")
        elif not _NAME_RE.match(last_name.strip()):
            errors.append("Nachname darf keine Sonderzeichen enthalten.")

        if not email.strip():
            errors.append("E-Mail ist ein Pflichtfeld.")
        elif not _EMAIL_RE.match(email.strip()):
            errors.append("Bitte eine gültige E-Mail-Adresse eingeben.")

        if not password:
            errors.append("Passwort ist ein Pflichtfeld.")
        else:
            if len(password) < 8:
                errors.append("Das Passwort muss mindestens 8 Zeichen lang sein.")
            if not _SPECIAL_RE.search(password):
                errors.append("Das Passwort muss mindestens ein Sonderzeichen enthalten (z.B. !@#$%).")

        if phone and not _PHONE_RE.match(phone.strip()):
            errors.append("Bitte eine gültige Telefonnummer eingeben (z.B. +41 79 123 45 67).")

        if errors:
            raise ValueError("\n".join(errors))

        if self.user_dao.get_by_email(email):
            raise ValueError("Ein Konto mit dieser E-Mail existiert bereits.")

        user = User(
            first_name=first_name.strip(),
            last_name=last_name.strip(),
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

    # ------------------------------------------------------------------
    # Delivery addresses

    def get_delivery_addresses(self, user_id: int) -> list[DeliveryAddress]:
        return self.address_dao.get_by_user(user_id)

    def add_delivery_address(
        self,
        user_id: int,
        street: str,
        house_nr: str,
        city: str,
        postal_code: str,
        floor: Optional[str] = None,
        label: Optional[str] = None,
    ) -> DeliveryAddress:
        if not all([street, house_nr, city, postal_code]):
            raise ValueError("Strasse, Hausnummer, Stadt und PLZ sind Pflichtfelder.")
        address = DeliveryAddress(
            user_id=user_id,
            label=label or None,
            street=street.strip(),
            house_nr=house_nr.strip(),
            floor=floor.strip() if floor else None,
            city=city.strip(),
            postal_code=postal_code.strip(),
        )
        return self.address_dao.create(address)

    def delete_delivery_address(self, address_id: int, user_id: int) -> bool:
        return self.address_dao.delete(address_id, user_id)

