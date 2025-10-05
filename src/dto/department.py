from pydantic import BaseModel
from typing import Optional
from uuid import UUID


class DepartmentBase(BaseModel):
    name: str


class DepartmentCreate(DepartmentBase):
    pass


class DepartmentUpdate(DepartmentBase):
    name: Optional[str] = None


class Department(DepartmentBase):
    id: UUID

    class Config:
        from_attributes = True
