from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import Optional
from src.database import get_db
from src.utils.auth import decode_access_token
from src.repository.worker_repository import WorkerRepository
from src.model.worker import Worker

# Configuración del esquema de seguridad Bearer
security = HTTPBearer()


async def get_current_worker(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> Worker:
    """
    Dependency para obtener el worker autenticado actual

    Extrae el token JWT del header Authorization,
    lo valida y retorna el worker autenticado

    Lanza HTTPException 401 si:
    - El token no es válido
    - El token ha expirado
    - El worker no existe en la base de datos
    """
    token = credentials.credentials

    # Decodificar el token
    payload = decode_access_token(token)

    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Obtener el worker_id del payload
    worker_id: str = payload.get("sub")

    if worker_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido - no contiene ID de usuario",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Buscar el worker en la base de datos
    worker_repo = WorkerRepository()
    worker = worker_repo.get_by_id(db, worker_id)

    if worker is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario no encontrado",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return worker


async def get_current_worker_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False)),
    db: Session = Depends(get_db)
) -> Optional[Worker]:
    """
    Dependency para obtener el worker autenticado actual (opcional)

    Similar a get_current_worker pero no lanza error si no hay token
    Útil para endpoints que funcionan con o sin autenticación
    """
    if credentials is None:
        return None

    try:
        return await get_current_worker(credentials, db)
    except HTTPException:
        return None


def require_role(*allowed_roles: str):
    """
    Decorator factory para requerir roles específicos

    Uso:
        @router.get("/admin-only")
        async def admin_endpoint(worker: Worker = Depends(require_role("admin"))):
            ...
    """
    async def role_checker(
        worker: Worker = Depends(get_current_worker)
    ) -> Worker:
        if worker.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Acceso denegado. Roles permitidos: {', '.join(allowed_roles)}"
            )
        return worker

    return role_checker
