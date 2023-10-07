import hashlib
import time

from shared.infrastructure import ErrorResponse, Measurement
from shared.utils import Utils

from .services.db_worker_service import DBWorkerService


class Functionalities:
    def _set_configs(self, db_service: DBWorkerService) -> None:
        self.db_error_details = db_service.get_error_details()
        if not self.db_error_details:
            raise ErrorResponse(100, "Error de conexión a mongo.",
                                self.transaction_id, 500,
                                code_name='500.general-error.100')

    def _error_attributes(self, error_code: int) -> dict:
        error_detail: dict = self.db_error_details[str(error_code)]
        code_name = error_detail['code_name']
        data = {'error_code': error_code,
                'message': error_detail['message'],
                'transaction_id': self.transaction_id,
                'status_code': int(code_name.split('.')[0]),
                'code_name': code_name}
        reference_code = error_detail.get('reference_code')
        if reference_code:
            data['reference_code'] = reference_code
        return data

    # Logic Functions ----------------------------------------------------------

    def _request_log_error(self, url: str, error_msg: str, time_elapsed: int,
                           error: str | Exception = '', method: str = 'GET',
                           object: dict = None) -> None:
        method_name = Utils.get_method_name(self, method.lower())
        measurement = Measurement(f"{method}: {url}", time_elapsed,
                                  "Error al consumir el servicio")
        self._log_external.error(error_msg, method_name, error,
                                 object, measurement)

    def _request_log_info(self, url: str, message: str, time_elapsed: int,
                          method: str = 'GET', object: dict = None) -> None:
        measurement = Measurement(f"{method}: {url}", time_elapsed)
        self._log_external.info(message, object, measurement)

    def _get_url(self, page=0, type_url='characters', id=None):
        ID = f'/{id}' if id else ''
        TIMESTAMP = int(time.time())
        LIMIT = f'limit=100&offset={page*100}'
        API_URL = 'http://gateway.marvel.com/v1/public'
        API_PUB_KEY = self._settings.MARVEL_API_PUBLIC_KEY
        API_PRIV_KEY = self._settings.MARVEL_API_PRIVATE_KEY

        KEYS = str(TIMESTAMP) + API_PRIV_KEY + API_PUB_KEY
        API_HASH = hashlib.md5(KEYS.encode("utf-8")).hexdigest()
        API_PARAMS = f'ts={TIMESTAMP}&apikey={API_PUB_KEY}&hash={API_HASH}'
        URL_CHARACTERS = f'{API_URL}/characters{ID}?{API_PARAMS}&orderBy=name&{LIMIT}'
        URL_COMICS = f'{API_URL}/comics{ID}?{API_PARAMS}&orderBy=title&format=comic&formatType=comic&noVariants=true&{LIMIT}'

        if type_url == 'characters':
            return URL_CHARACTERS

        return URL_COMICS
