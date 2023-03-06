from functools import wraps

from fastapi import Depends, Header, HTTPException, Request
from fastapi.security import HTTPAuthorizationCredentials
from fastapi_jwt_auth import AuthJWT
import httpx

from core.config import jwt_settings


class AuthService:
    def __call__(self, auth: AuthJWT = Depends()):
        auth.jwt_required()
        user_id = auth.get_jwt_subject()
        return user_id


auth_service = AuthService()


async def _user_has_role(user_id, role_name, x_request_id, jwt) -> bool:
    auth_api_base_url = (
        jwt_settings.auth_api_base_url
        + jwt_settings.auth_api_roles_check_endpoint_url
    )
    full_auth_api_url = f"{auth_api_base_url}{role_name}/{user_id}/check"
    print(full_auth_api_url)
    headers = {
        "Authorization": jwt,
        "X-Request-Id": x_request_id,
    }
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(full_auth_api_url, headers=headers)
            response_json = response.json()
            if response_json.get("success"):
                return True
            else:
                raise HTTPException(
                    status_code=403,
                    detail="User does not have necessary roles",
                )
    except httpx.HTTPError as e:
        print(e)
        raise HTTPException(
            status_code=500, detail="Unable to authenticate user"
        )


def has_role(allowed_role: str):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, request: Request, **kwargs):
            headers = dict(request.headers)
            print(
                f'user id = {None}, authorization = {headers["authorization"]} --------------------------------------------------'
            )
            user_has_role = await _user_has_role(
                "317d91d6-8321-47d8-9352-9886aca616d8",
                allowed_role,
                headers["x-request-id"],
                headers["authorization"],
            )
            if user_has_role:
                return await func(*args, **kwargs)
            else:
                raise HTTPException(status_code=403, detail="Not authorized")

        return wrapper

    return decorator
