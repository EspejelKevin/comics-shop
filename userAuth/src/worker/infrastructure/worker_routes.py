import autodynatrace
from fastapi import APIRouter
from shared.infrastructure import HttpResponse
from shared.infrastructure.settings import get_settings
from worker.domain import UserInput
from worker.infrastructure import WorkerController

settings = get_settings()

version = settings.API_VERSION
namespace = settings.NAMESPACE
prefix = f'/{namespace}/api/{version}'

descriptions = {
    'liveness': 'Verifica que el servicio se encuentre disponible.',
    'readiness': 'Verifica que existan conexiones activas a MONGO/REDIS/FIREBASE.',
    'signup': 'Registra un nuevo usuario en base de datos.'
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
def signup(user: UserInput) -> HttpResponse:
    return WorkerController.signup(user)
