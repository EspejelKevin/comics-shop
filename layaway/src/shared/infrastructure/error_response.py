from .settings import get_settings

settings = get_settings()
developer_portal_errors_url = settings.DEVELOPER_PORTAL_HTTP_ERRORS


class ErrorResponse(Exception):
    def __init__(self, error_code: int | str, message: str,
                 transaction_id: str, status_code: int = 500,
                 code_name: str = '', reference_code: str = None,
                 **kwargs) -> None:
        self.status_code = status_code
        self.data = {
            'user_message': message
        }
        self.meta = {
            'error_code': int(error_code),
            'info': f'{developer_portal_errors_url}#{code_name}',
            'reference_code': reference_code,
            'transaction_id': transaction_id,
            **kwargs
        }
