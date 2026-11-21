from pydantic import BaseModel, EmailStr
from typing import Optional

class UserRegister(BaseModel):
    username: str
    email: EmailStr
    phone_number: Optional[str] = None
    password: str
    confirm_password: str