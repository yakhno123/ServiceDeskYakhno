from datetime import datetime
from enum import Enum as PyEnum
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum
from werkzeug.security import generate_password_hash, check_password_hash

from app.database import Base


class UserRole(PyEnum):
    CLIENT = "client"
    ADMIN = "admin"
    MASTER = "master"
    SUPPLIER = "supplier"


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(80), unique=True, nullable=False, index=True)
    email = Column(String(120), unique=True, nullable=False, index=True)
    phone_number = Column(String(20), nullable=True)
    hashed_password = Column(String(255), nullable=False)

    role = Column(Enum(UserRole), default=UserRole.CLIENT, nullable=False)
    is_active = Column(Boolean, default=True)

    telegram_id = Column(String(50), nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)

    def set_password(self, password: str):
        self.hashed_password = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.hashed_password, password)