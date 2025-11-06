# Autenticación JWT - Cursito API

## Descripción

Se ha implementado un sistema de autenticación completo basado en JWT (JSON Web Tokens) para proteger los endpoints de la API.

## Características

- ✅ Autenticación basada en JWT
- ✅ Hash seguro de contraseñas con bcrypt
- ✅ Tokens con expiración configurable (30 minutos por defecto)
- ✅ Middleware de autenticación reutilizable
- ✅ Control de acceso basado en roles
- ✅ Endpoints protegidos y públicos

## Configuración

### Variables de Entorno (.env)

```env
JWT_SECRET_KEY=supersecretkey-change-this-in-production-use-random-string
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
```

**IMPORTANTE:** Cambia `JWT_SECRET_KEY` en producción por una clave secreta segura y aleatoria.

## Endpoints de Autenticación

### 1. Login - POST /auth/login

Autentica un usuario y retorna un token JWT.

**Request:**
```json
{
  "email": "usuario@veracruz.tecnm.mx",
  "password": "mipassword123"
}
```

**Response (200 OK):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 30,
  "worker_id": "123e4567-e89b-12d3-a456-426614174000",
  "email": "usuario@veracruz.tecnm.mx",
  "role": "teacher",
  "department_id": "123e4567-e89b-12d3-a456-426614174001"
}
```

**Response (401 Unauthorized):**
```json
{
  "detail": "Credenciales incorrectas"
}
```

### 2. Obtener Usuario Actual - GET /auth/me

Obtiene la información del usuario autenticado.

**Headers:**
```
Authorization: Bearer <token>
```

**Response (200 OK):**
```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "email": "usuario@veracruz.tecnm.mx",
  "name": "Juan",
  "father_lastname": "Pérez",
  "mother_lastname": "García",
  "role": "teacher",
  "department_id": "123e4567-e89b-12d3-a456-426614174001",
  "rfc": "PEGJ850101ABC",
  "curp": "PEGJ850101HVZRXN01",
  "sex": "M",
  "phone": "2281234567"
}
```

### 3. Cambiar Contraseña - POST /auth/change-password

Permite al usuario autenticado cambiar su contraseña.

**Headers:**
```
Authorization: Bearer <token>
```

**Request:**
```json
{
  "current_password": "oldpassword123",
  "new_password": "newpassword456"
}
```

**Response (200 OK):**
```json
{
  "message": "Contraseña actualizada exitosamente"
}
```

## Uso del Middleware de Autenticación

### Proteger un Endpoint (Requiere Autenticación)

```python
from fastapi import APIRouter, Depends
from src.middleware.auth_middleware import get_current_worker
from src.model.worker import Worker

router = APIRouter()

@router.get("/protected-endpoint")
async def protected_route(current_worker: Worker = Depends(get_current_worker)):
    return {
        "message": f"Hola {current_worker.name}",
        "worker_id": str(current_worker.id)
    }
```

### Proteger con Rol Específico

```python
from src.middleware.auth_middleware import require_role

@router.delete("/admin-only/{id}")
async def admin_only_route(
    id: str,
    current_worker: Worker = Depends(require_role("admin"))
):
    # Solo usuarios con role="admin" pueden acceder
    return {"message": "Acción ejecutada por admin"}
```

### Autenticación Opcional

```python
from src.middleware.auth_middleware import get_current_worker_optional

@router.get("/optional-auth")
async def optional_auth_route(
    current_worker: Worker = Depends(get_current_worker_optional)
):
    if current_worker:
        return {"message": f"Autenticado como {current_worker.name}"}
    else:
        return {"message": "Usuario anónimo"}
```

## Ejemplos de Uso con cURL

### Login
```bash
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "usuario@veracruz.tecnm.mx",
    "password": "mipassword123"
  }'
```

### Acceder a Endpoint Protegido
```bash
curl -X GET "http://localhost:8000/auth/me" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

### Cambiar Contraseña
```bash
curl -X POST "http://localhost:8000/auth/change-password" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -d '{
    "current_password": "oldpassword123",
    "new_password": "newpassword456"
  }'
```

## Ejemplos de Uso con JavaScript/Fetch

### Login
```javascript
const response = await fetch('http://localhost:8000/auth/login', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    email: 'usuario@veracruz.tecnm.mx',
    password: 'mipassword123'
  })
});

const data = await response.json();
const token = data.access_token;

// Guardar token en localStorage
localStorage.setItem('token', token);
```

### Acceder a Endpoint Protegido
```javascript
const token = localStorage.getItem('token');

const response = await fetch('http://localhost:8000/auth/me', {
  headers: {
    'Authorization': `Bearer ${token}`
  }
});

const userData = await response.json();
console.log(userData);
```

## Generar Hash de Contraseña

Para crear un usuario nuevo o actualizar contraseñas, usa el script incluido:

```bash
cd cursito-api
python hash_password.py
```

Luego inserta el hash en la base de datos:

```sql
UPDATE worker
SET password = '$2b$12$...'
WHERE email = 'usuario@veracruz.tecnm.mx';
```

## Estructura de Archivos Creados

```
cursito-api/
├── src/
│   ├── controller/
│   │   └── auth_controller.py          # Endpoints de autenticación
│   ├── dto/
│   │   └── auth.py                      # DTOs para autenticación
│   ├── middleware/
│   │   └── auth_middleware.py           # Middleware JWT y decoradores
│   └── utils/
│       └── auth.py                      # Utilidades de hash y JWT
├── hash_password.py                     # Script para generar hashes
├── .env                                 # Variables de entorno JWT
└── AUTH_README.md                       # Esta documentación
```

## Seguridad

### Mejores Prácticas Implementadas

1. ✅ Contraseñas hasheadas con bcrypt
2. ✅ Tokens JWT con expiración
3. ✅ Validación de tokens en cada request
4. ✅ Manejo seguro de credenciales
5. ✅ Headers WWW-Authenticate en respuestas 401

### Recomendaciones para Producción

1. **Cambiar JWT_SECRET_KEY**: Usa una clave aleatoria y segura
2. **HTTPS**: Implementa SSL/TLS en producción
3. **CORS**: Configura orígenes permitidos específicos
4. **Rate Limiting**: Implementa límite de intentos de login
5. **Refresh Tokens**: Considera implementar refresh tokens para sesiones largas
6. **Logging**: Registra intentos de autenticación fallidos

## Testing

Para probar la autenticación, visita la documentación interactiva:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

En Swagger UI puedes:
1. Hacer login en `/auth/login`
2. Copiar el `access_token`
3. Hacer clic en el botón "Authorize" (🔓)
4. Pegar el token en el campo `Value` como: `Bearer <tu-token>`
5. Probar endpoints protegidos

## Roles Disponibles

Los roles se almacenan en el campo `role` del modelo Worker:

- `admin` - Administrador del sistema
- `teacher` - Profesor/Instructor
- `coordinator` - Coordinador de departamento
- `student` - Estudiante (si aplica)

Puedes extender esta lista según tus necesidades.

## Troubleshooting

### Error: "Token inválido o expirado"
- Verifica que el token no haya expirado (30 min por defecto)
- Asegúrate de incluir "Bearer " antes del token
- Verifica que JWT_SECRET_KEY sea la misma en .env

### Error: "Credenciales incorrectas"
- Verifica que el email exista en la base de datos
- Asegúrate de que la contraseña esté hasheada correctamente
- Usa `hash_password.py` para generar hashes válidos

### Error: "Usuario no encontrado"
- El token es válido pero el worker_id no existe
- Verifica que el usuario no haya sido eliminado de la BD

## Soporte

Para más información sobre FastAPI Security:
- https://fastapi.tiangolo.com/tutorial/security/
- https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/
