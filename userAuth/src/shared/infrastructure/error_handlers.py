import uuid

from fastapi import HTTPException
from fastapi.exceptions import RequestValidationError
from shared.domain import FailureResponse
from shared.utils import Utils

from .cache_config import CachedConfig
from .error_response import ErrorResponse
from .http_response import HttpResponse
from .settings import get_settings

settings = get_settings()
developer_portal_errors_url = settings.DEVELOPER_PORTAL_HTTP_ERRORS


# Error Response:
def error_exception_handler(_, ex: ErrorResponse) -> HttpResponse:
    content = FailureResponse(ex.data, ex.status_code, **ex.meta)
    return HttpResponse(content=content, status_code=ex.status_code,
                        excludes={'_status_code'})


# Error 401: Unauthorized.
def unauthorized_exception_handler(_, _ex: HTTPException) -> HttpResponse:
    return get_error_response(104, _ex.detail)


# Error 500: Internal Server Error
def internal_server_error_exception_handler(_, _ex: Exception) -> HttpResponse:
    return get_error_response(105)


# Error 400: Invalid Parameters.
def parameter_exception_handler(_, _ex: RequestValidationError) -> HttpResponse:
    details = Utils.get_error_details(_ex.errors())
    return get_error_response(106, details)


# Error 404: Page Not Found.
def not_found_error_exception_handler(_, _ex: HTTPException) -> HttpResponse:
    return get_error_response(107)


# Error 405: Method Not Allowed.
def method_not_allowed_exception_handler(_, _ex: HTTPException) -> HttpResponse:
    return get_error_response(108)


def get_error_response(error_code: int, details: dict = None):
    error = get_error_detail(error_code)
    status_code = int(error['code_name'].split('.')[0])
    data = {'user_message': error['message']}
    meta = {
        'details': details,
        'error_code': error_code,
        'info': f'{developer_portal_errors_url}#'
                f'{error["code_name"]}',
        'transaction_id': uuid.uuid4()
    }
    content = FailureResponse(data, status_code, **meta)
    return HttpResponse(content=content, status_code=status_code,
                        excludes={'_status_code'})


def get_error_detail(code_name: int) -> dict:
    error_details = CachedConfig.get_cached_responses(
        'MongoWorkerRepository.get_error_details')
    return error_details['data'][str(code_name)]
