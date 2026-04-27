from pydantic import BaseModel


class AuthLoginDTO(BaseModel):
    username: str
    password: str
