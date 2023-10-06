import autodynatrace
from fastapi import APIRouter, Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from shared.infrastructure import HttpResponse
from shared.infrastructure.settings import get_settings
from worker.domain import UserLogin, UserRegistration
from worker.infrastructure import WorkerController

settings = get_settings()

version = settings.API_VERSION
namespace = settings.NAMESPACE
prefix = f'/{namespace}/api/{version}'

descriptions = {
    'liveness': 'Verifica que el servicio se encuentre disponible.',
    'readiness': 'Verifica que existan conexiones activas a MONGO/REDIS/FIREBASE.',
    'signup': 'Registra un nuevo usuario en base de datos.',
    'login': 'Verifica si un usuario existe en base de datos.',
    'keys': 'Valida si el token es correcto y retorna el payload'
}

router = APIRouter(prefix=prefix)


@router.get('/liveness', tags=['Health Checks'],
            summary=descriptions['liveness'])
@autodynatrace.trace(f'{prefix}/liveness')
def liveness() -> dict:
    return {'status': 'success'}


@router.get('/readiness', tags=['Health Checks'],
            summary=descriptions['readiness'])
@autodynatrace.trace(f'{prefix}/readiness')
def readiness() -> HttpResponse:
    return WorkerController.readiness()


@router.post('/signup', tags=['Auth'],
             summary=descriptions['signup'])
@autodynatrace.trace(f'{prefix}/signup')
def signup(user: UserRegistration) -> HttpResponse:
    return WorkerController.signup(user)


@router.post('/login', tags=['Auth'],
             summary=descriptions['login'])
@autodynatrace.trace(f'{prefix}/login')
def login(user: UserLogin) -> HttpResponse:
    return WorkerController.login(user)


@router.get('/keys', tags=['Auth'],
            summary=descriptions['keys'])
@autodynatrace.trace(f'{prefix}/keys')
def keys(authorization: HTTPAuthorizationCredentials = Depends(HTTPBearer())) -> HttpResponse:
    token = authorization.credentials
    return WorkerController.keys(token)
