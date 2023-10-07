import container
import uvicorn
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from shared.infrastructure import (ErrorResponse, error_exception_handler,
                                   internal_server_error_exception_handler,
                                   method_not_allowed_exception_handler,
                                   not_found_error_exception_handler,
                                   parameter_exception_handler,
                                   unauthorized_exception_handler)
from shared.infrastructure.settings import get_settings
from worker.infrastructure import router
from worker.infrastructure.worker_controller import WorkerController

settings = get_settings()

namespace = settings.NAMESPACE
api_version = settings.API_VERSION
resource = settings.RESOURCE
enable_docs = settings.ENABLE_DOCS

prefix = f'/{namespace}/api/{api_version}/{resource}'

description = '''

    Creado con FastAPI y Arquitectura Hexagonal.
    Python: 3.11.0

**Permite obtener un listado de Detalles de Comics con posible filtrado por
nombre de personajes o titulo de comic.**
'''

tags_metadata = [
    {
        'name': 'Health Checks',
        'description': 'Comprobaciones de estado para la obtención de datos '
                       'sobre el estado, disponibilidad y latencia en tiempo real.',
    },
    {
        'name': 'Comics',
        'description': 'Permite obtener un listado de Comics.',
    }
]


def on_start_up() -> None:
    container.SingletonContainer.init()
    WorkerController.update_cache()


exception_handlers = {
    403: unauthorized_exception_handler,
    404: not_found_error_exception_handler,
    405: method_not_allowed_exception_handler,
    500: internal_server_error_exception_handler
}

app = FastAPI(
    title=settings.SERVICE_NAME,
    description=description,
    version=settings.IMAGE_VERSION,
    openapi_tags=tags_metadata,
    docs_url=f'{prefix}/docs' if enable_docs else None,
    openapi_url=f'{prefix}/openapi.json' if enable_docs else None,
    redoc_url=f'{prefix}/redoc' if enable_docs else None,
    exception_handlers=exception_handlers,
    on_startup=[on_start_up])

app.add_exception_handler(ErrorResponse, error_exception_handler)
app.add_exception_handler(RequestValidationError, parameter_exception_handler)
app.include_router(router)

if __name__ == '__main__':
    uvicorn.run('main:app', host='0.0.0.0',
                port=settings.PORT, reload=settings.RELOAD)
