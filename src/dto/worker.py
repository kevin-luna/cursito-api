from pydantic import BaseModel, EmailStr
from typing import Optional
from uuid import UUID


class WorkerBase(BaseModel):
    department_id: UUID
    rfc: str
    curp: str
    sex: int  # 0 = mujer, 1 = hombre
    telephone: Optional[str] = None
    email: EmailStr
    name: str
    fathers_surname: str
    mother_surname: Optional[str] = None
    role: int  # 0 = docente, 1 = jefe de departamento


class WorkerCreate(WorkerBase):
    password: str


class WorkerUpdate(BaseModel):
    department_id: Optional[UUID] = None
    rfc: Optional[str] = None
    curp: Optional[str] = None
    sex: Optional[int] = None
    telephone: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    name: Optional[str] = None
    fathers_surname: Optional[str] = None
    mother_surname: Optional[str] = None
    role: Optional[int] = None


class Worker(WorkerBase):
    id: UUID

    class Config:
        from_attributes = True


class WorkerResponse(Worker):
    password: str  # Include password in response for admin purposes
