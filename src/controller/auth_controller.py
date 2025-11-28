from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from src.database import get_db
from src.dto.auth import LoginRequest, TokenResponse, ChangePasswordRequest
from src.repository.worker_repository import WorkerRepository
from src.utils.auth import (
    verify_password,
    get_password_hash,
    create_access_token,
    ACCESS_TOKEN_EXPIRE_MINUTES
)
from src.middleware.auth_middleware import get_current_worker
from src.model.worker import Worker
from ..dto.worker import WorkerUpdate

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/login", response_model=TokenResponse, status_code=status.HTTP_200_OK)
async def login(
    login_data: LoginRequest,
    db: Session = Depends(get_db)
):
    """
    Endpoint de login - Autentica un usuario y retorna un token JWT

    - **email**: Correo electrónico del usuario (debe existir en la base de datos)
    - **password**: Contraseña del usuario

    Retorna un token JWT válido por 30 minutos (configurable)
    """
    worker_repo = WorkerRepository()

    # Buscar el worker por email
    worker = worker_repo.get_by_email(db, login_data.email)

    if not worker:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Verificar la contraseña
    if not verify_password(login_data.password, worker.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Crear el token JWT
    token_data = {
        "sub": str(worker.id),
        "email": worker.email,
        "position": worker.position,
        "department_id": str(worker.department_id) if worker.department_id else None
    }

    access_token = create_access_token(data=token_data)

    # Retornar la respuesta
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES,
        worker_id=str(worker.id),
        email=worker.email,
        position=str(worker.position),
        department_id=str(worker.department_id) if worker.department_id else None
    )


@router.post("/change-password", status_code=status.HTTP_200_OK)
async def change_password(
    password_data: ChangePasswordRequest,
    current_worker: Worker = Depends(get_current_worker),
    db: Session = Depends(get_db)
):
    """
    Endpoint para cambiar la contraseña del usuario autenticado

    Requiere autenticación JWT

    - **current_password**: Contraseña actual
    - **new_password**: Nueva contraseña (mínimo 8 caracteres)
    """
    # Verificar la contraseña actual
    if len(password_data.new_password) < 8:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La longitud de la contraseña debe ser de al menos 8 caracteres."
        )

    # Verificar la contraseña actual
    if not verify_password(password_data.current_password, current_worker.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La contraseña actual es incorrecta"
        )

    # Actualizar la contraseña
    worker_repo = WorkerRepository()
    current_worker.password = get_password_hash(password_data.new_password)
    worker_repo.update(db,current_worker, WorkerUpdate(password=password_data.new_password))

    return {
        "message": "Contraseña actualizada exitosamente"
    }


@router.get("/me", status_code=status.HTTP_200_OK)
async def get_current_user_info(
    current_worker: Worker = Depends(get_current_worker)
):
    """
    Endpoint para obtener información del usuario autenticado

    Requiere autenticación JWT

    Retorna los datos del trabajador actualmente autenticado
    """
    return {
        "id": str(current_worker.id),
        "email": current_worker.email,
        "name": current_worker.name,
        "father_surname": current_worker.father_surname,
        "mother_surname": current_worker.mother_surname,
        "position": current_worker.position,
        "department_id": str(current_worker.department_id) if current_worker.department_id else None,
        "rfc": current_worker.rfc,
        "curp": current_worker.curp,
        "sex": current_worker.sex,
        "telephone": current_worker.telephone
    }
