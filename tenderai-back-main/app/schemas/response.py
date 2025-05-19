from __future__ import annotations
from pydantic import BaseModel, ConfigDict
from typing import Generic, TypeVar, Optional

T = TypeVar("T")

class ResponseModel(BaseModel, Generic[T]):
    success: bool = True
    message: Optional[str] = None
    data: Optional[T] = None

    model_config = ConfigDict(from_attributes=True)