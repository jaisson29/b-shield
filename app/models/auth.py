from pydantic import BaseModel


class Token(BaseModel):
    access_token: str
    token_type: str

class UserInfo(BaseModel):
    sub: str
    rol: str
    nombre: str
