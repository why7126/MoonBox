from typing import Generic, TypeVar

from pydantic import BaseModel

DataT = TypeVar("DataT")


class ApiResponse(BaseModel, Generic[DataT]):
    code: int = 0
    message: str = "success"
    data: DataT


class PageResponse(BaseModel, Generic[DataT]):
    items: list[DataT]
    total: int
    page: int
    page_size: int


class ErrorResponse(BaseModel):
    code: int
    message: str
    data: dict[str, str] | None = None
