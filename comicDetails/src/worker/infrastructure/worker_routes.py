import autodynatrace
from fastapi import APIRouter, Depends
from shared.infrastructure import HttpResponse
from shared.infrastructure.settings import get_settings
from worker.domain import Filter
from worker.infrastructure import WorkerController

# serviceName:
# /namespace/v1/resource

settings = get_settings()

version = settings.API_VERSION
namespace = settings.NAMESPACE
resource = settings.RESOURCE
prefix = f'/{namespace}/api/{version}/{resource}'

descriptions = {
    'liveness': 'Verifica que el servicio se encuentre disponible.',
    'readiness': 'Verifica que existan conexiones activas a MONGO/REDIS/FIREBASE.',
    'get_records': 'Devuelve un listado de personajes o comics.',
    'get_record': 'Devuelve un personaje o un comic por ID.'
}

router = APIRouter(prefix=prefix)


@router.get('/liveness', tags=['Health Checks'],
            summary=descriptions['liveness'])
@autodynatrace.trace(f'{prefix}/liveness')
def liveness() -> dict:
    return {'status': 'Success'}


@router.get('/readiness', tags=['Health Checks'],
            summary=descriptions['readiness'])
@autodynatrace.trace(f'{prefix}/readiness')
def readiness() -> HttpResponse:
    return WorkerController.readiness()


@router.get('', tags=['Comics'],
            summary=descriptions['get_records'])
@autodynatrace.trace(f'{prefix}')
def get_records(filter: Filter = Depends()) -> HttpResponse:
    ''' Devuelve todo un listado de personajes y/o comics. '''
    return WorkerController.get_records(filter)


@router.get('/{id}', tags=['Comics'],
            summary=descriptions['get_record'])
@autodynatrace.trace(f'{prefix}/<id>')
def get_record(id: int) -> HttpResponse:
    ''' Devuelve un personaje o un comic por su ID. '''
    return WorkerController.get_record(id)
