import re
from pydantic import (
    BaseModel,
    EmailStr,
    Field,
    field_validator
)


class UserRegister(BaseModel):
    full_name: str = Field(examples=["Alba Alvarado"])
    email: EmailStr = Field(..., description="Valid email address")
    password: str = Field(examples=["Alb@1sL0v3"])
    phone: str = Field(examples=["987654321"])
    
    @field_validator("phone")
    def phone_validator(cls, v: str):
        if len(v) != 9 or not v.startswith("9"):
            raise ValueError("Number must be peruvian")
        return v
    
    @field_validator("full_name")
    def name_max(cls, v):
        if len(v) > 255:
            raise ValueError("Full Name must be at most 255 characters.")
        return v

    @field_validator("password")
    def password_complexity(cls, v):
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters.")

        if not re.search(r"[a-z]", v):
            raise ValueError("Password must contain at least one lowercase "
                             "letter.")

        if not re.search(r"[A-Z]", v):
            raise ValueError("Password must contain at least one uppercase "
                             "letter.")

        if not re.search(r"\d", v):
            raise ValueError("Password must contain at least one number.")

        if not re.search(r"[@$!%*?&]", v):
            raise ValueError("Password must contain at least one special "
                             "character.")
        return v


class UserLogin(BaseModel):
    email: EmailStr = Field(..., description="Valid email address")
    password: str = Field(examples=["Alb@1sL0v3"])

    @field_validator("password")
    def password_complexity(cls, v):
        if len(v) < 8:
            raise ValueError("Invalid password")

        if not re.search(r"[a-z]", v):
            raise ValueError("Invalid password")

        if not re.search(r"[A-Z]", v):
            raise ValueError("Invalid password")

        if not re.search(r"\d", v):
            raise ValueError("Invalid password")

        if not re.search(r"[@$!%*?&]", v):
            raise ValueError("Invalid password")
        return v


class JWTResponse(BaseModel):
    access_token: str
    refresh_token: str


class JWTRefresh(BaseModel):
    refresh_token: str
