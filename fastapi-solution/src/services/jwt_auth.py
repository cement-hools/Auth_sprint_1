from fastapi import Depends
from fastapi_jwt_auth import AuthJWT


class AuthService:
    def __call__(self, auth: AuthJWT = Depends()):
        auth.jwt_required()
        user_id = auth.get_jwt_subject()
        return user_id


auth_service = AuthService()
