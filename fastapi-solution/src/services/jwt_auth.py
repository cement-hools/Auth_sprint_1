from functools import wraps
import base64
import json

from fastapi import Depends, HTTPException, Request
from fastapi_jwt_auth import AuthJWT
import httpx

from core.config import jwt_settings


class AuthService:
    def __call__(self, auth: AuthJWT = Depends()):
        auth.jwt_required()
        user_id = auth.get_jwt_subject()
        return user_id


auth_service = AuthService()


def _extract_sub(auth_header):
    """
    Extracts the 'sub' field from a JWT token without using external libraries.
    TODO: use fastapi_jwt_auth for this somehow
    """
    token = auth_header.split(" ")[1]
    token_parts = token.split(".")
    payload = token_parts[1]

    # add padding to the base64-encoded payload if needed
    padding = len(payload) % 4
    if padding > 0:
        payload += "=" * (4 - padding)

    # decode the base64-encoded payload
    decoded_payload = base64.urlsafe_b64decode(payload)

    # convert the decoded payload from bytes to a string
    decoded_payload_str = decoded_payload.decode("utf-8")

    # parse the decoded payload as JSON and extract the 'sub' field
    payload_dict = json.loads(decoded_payload_str)
    return payload_dict["sub"]


async def _user_has_role(user_id, role_name, x_request_id, jwt) -> bool:
    auth_api_base_url = (
        jwt_settings.auth_api_base_url
        + jwt_settings.auth_api_roles_check_endpoint_url
    )
    full_auth_api_url = f"{auth_api_base_url}{role_name}/{user_id}/check"
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
    except httpx.HTTPError:
        raise HTTPException(
            status_code=500, detail="Unable to authenticate user"
        )


def has_role(allowed_role: str):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, request: Request, **kwargs):
            headers = dict(request.headers)
            user_id = _extract_sub(headers["authorization"])

            user_has_role = await _user_has_role(
                user_id,
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
