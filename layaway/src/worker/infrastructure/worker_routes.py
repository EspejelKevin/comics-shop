import autodynatrace
from fastapi import APIRouter, Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from shared.infrastructure import HttpResponse
from shared.infrastructure.settings import get_settings
from worker.domain import ComicInput, Filter
from worker.infrastructure import WorkerController

settings = get_settings()

version = settings.API_VERSION
namespace = settings.NAMESPACE
prefix = f'/{namespace}/api/{version}/layaway'

descriptions = {
    'liveness': 'Verifica que el servicio se encuentre disponible.',
    'readiness': 'Verifica que existan conexiones activas a MONGO/REDIS/FIREBASE.',
    'related': 'Realiza la relación entre comics y un usuario.',
    'get_related': 'Obtiene el apartado de un usuario'
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


@router.post('', tags=['Layaway'], summary=descriptions['related'])
@autodynatrace.trace(f'{prefix}')
def related_comics(comic_input: ComicInput,
                   authorization: HTTPAuthorizationCredentials = Depends(HTTPBearer())) -> HttpResponse:
    token = authorization.credentials
    return WorkerController.related_comics(comic_input, token)


@router.get('', tags=['Layaway'], summary=descriptions['get_related'])
@autodynatrace.trace(f'{prefix}')
def related_comics(filter: Filter = Depends(),
                   authorization: HTTPAuthorizationCredentials = Depends(HTTPBearer())) -> HttpResponse:
    token = authorization.credentials
    return WorkerController.get_related_comics(filter, token)
