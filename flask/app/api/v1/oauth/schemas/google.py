from pydantic import BaseModel, EmailStr, AnyUrl


class Token(BaseModel):
    sub: str
    email: EmailStr
    email_verified: bool
