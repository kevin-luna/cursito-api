from typing import List, TypeVar, Generic
from pydantic import BaseModel

T = TypeVar('T')

class PaginatedResponse(BaseModel, Generic[T]):
    items: List[T]
    total_pages: int
    page: int
    total_count: int

    model_config = {"from_attributes": True}
