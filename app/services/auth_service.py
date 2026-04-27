from datetime import timezone


class AuthService:

    def verify_token(self, token: str) -> dict:
        from app.middleware.auth import VALID_TOKENS

        if token in VALID_TOKENS:
            return VALID_TOKENS[token]

        user = self.decode_token(token)
        return user

    def is_admin(self, user: dict) -> bool:
        return user.get("rol") == "admin"

    def generate_token(self, user_info: dict) -> str:
        from jwt import PyJWT
        import os
        from datetime import datetime, timedelta

        payload = {
            "sub": user_info.get("sub"),
            "rol": user_info.get("rol"),
            "nombre": user_info.get("nombre"),
            "exp": datetime.now(tz=timezone.utc)
            + timedelta(days=1),  # Token expira en 1 día
        }
        token = PyJWT().encode(
            payload, os.getenv("JWT_SECRET_KEY", "default_secret"), algorithm="HS256"
        )
        return token

    def decode_token(self, token: str) -> dict:
        from jwt import PyJWT
        import os

        user = PyJWT().decode(
            token, os.getenv("JWT_SECRET_KEY", "default_secret"), algorithms=["HS256"]
        )
        return user
