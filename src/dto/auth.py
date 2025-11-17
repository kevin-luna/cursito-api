from pydantic import BaseModel, EmailStr, Field
from typing import Optional


class LoginRequest(BaseModel):
    """
    DTO para la solicitud de login
    """
    email: EmailStr = Field(..., description="Correo electrónico del usuario")
    password: str = Field(..., min_length=1, description="Contraseña del usuario")

    model_config = {
        "json_schema_extra": {
            "example": {
                "email": "usuario@veracruz.tecnm.mx",
                "password": "mipassword123"
            }
        }
    }


class TokenResponse(BaseModel):
    """
    DTO para la respuesta del token JWT
    """
    access_token: str = Field(..., description="Token JWT de acceso")
    token_type: str = Field(default="bearer", description="Tipo de token")
    expires_in: int = Field(..., description="Tiempo de expiración en minutos")
    worker_id: str = Field(..., description="ID del trabajador autenticado")
    email: str = Field(..., description="Email del trabajador")
    position: str = Field(..., description="Posición del trabajador")
    department_id: Optional[str] = Field(None, description="ID del departamento")

    model_config = {
        "json_schema_extra": {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
                "expires_in": 30,
                "worker_id": "123e4567-e89b-12d3-a456-426614174000",
                "email": "usuario@veracruz.tecnm.mx",
                "role": "teacher",
                "department_id": "123e4567-e89b-12d3-a456-426614174001"
            }
        }
    }


class TokenPayload(BaseModel):
    """
    DTO para el payload del token JWT
    """
    sub: str  # worker_id
    email: str
    position: str
    department_id: Optional[str] = None
    exp: Optional[int] = None


class ChangePasswordRequest(BaseModel):
    """
    DTO para cambiar contraseña
    """
    current_password: str = Field(..., min_length=1, description="Contraseña actual")
    new_password: str = Field(..., min_length=8, description="Nueva contraseña (mínimo 8 caracteres)")

    model_config = {
        "json_schema_extra": {
            "example": {
                "current_password": "oldpassword123",
                "new_password": "newpassword456"
            }
        }
    }
