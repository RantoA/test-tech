from pydantic import BaseModel


class ApiResponse[T](BaseModel):
    """Uniform JSON envelope returned by every endpoint."""

    status: int
    message: str
    data: T | None = None
