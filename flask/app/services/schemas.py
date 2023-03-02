from typing import Any

from pydantic import BaseModel


class ServiceResult(BaseModel):
    success: bool
    error_message: str | None
    data: Any | None
