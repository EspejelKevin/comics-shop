import container
import uvicorn
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from shared.infrastructure import (ErrorResponse, error_exception_handler,
                                   get_settings,
                                   internal_server_error_exception_handler,
                                   method_not_allowed_exception_handler,
                                   not_found_error_exception_handler,
                                   parameter_exception_handler,
                                   unauthorized_exception_handler)
from worker.infrastructure import WorkerController, router

settings = get_settings()

namespace = settings.NAMESPACE
api_version = settings.API_VERSION
enable_docs = settings.ENABLE_DOCS

prefix = f'/{namespace}/api/{api_version}/layaway'


description = '''

    Creado con FastAPI y Arquitectura Hexagonal.
    Python: 3.11.0

**Microservicio encargado de regristar comics para un usuario en particular.**
'''

tags_metadata = [
    {
        'name': 'Health Checks',
        'description': 'Comprobaciones de estado para la obtención de datos '
                       'sobre el estado, disponibilidad y latencia en tiempo real.',
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
