import asyncio
import copy
import time
import uuid

from shared.domain import Response, SuccessResponse
from shared.infrastructure import (ErrorResponse, GeneralRequestServer, Log,
                                   Measurement, Settings)
from shared.utils import Utils
from worker.application import Functionalities
from worker.domain import ComicInput, DBRepository


class RelatedComicsUsecase(Functionalities):
    def __init__(self, db_worker_service: DBRepository, log: Log,
                 settings: Settings) -> None:
        self.__db_service = db_worker_service
        self._log = log
        self.settings = settings
        self.transaction_id = str(uuid.uuid4())
        self._general_request = GeneralRequestServer()

    def execute(self, comic_input: ComicInput, token: str) -> Response:
        init_time = time.perf_counter()
        self._set_logs()

        self._log.info('Start: Related Comics Usecase',
                       object=comic_input.dict())

        self._set_configs(self.__db_service)

        message = self._get_response(comic_input, token)
        response = {'message': message}

        time_elapsed = Utils.get_time_elapsed_ms(init_time)
        self._log.info('RelatedComics: successfully')

        return SuccessResponse(response, 200, self.transaction_id, time_elapsed)

    def _get_response(self, comic_input: ComicInput, token: str) -> str:
        method_name = Utils.get_method_name(self, '_get_response')
        comic_id = comic_input.id
        user = self._validate_token(token)
        comic = self._get_comic_to_link(comic_id)
        user_id = user.get('id')
        username = user.get('username')

        user_comics = self.__db_service.get_user_comics(user_id)

        if user_comics is None:
            self._create_measurement(
                'MongoDB', 'Failed to get comics from Mongo', 'Mongo is not up', method_name)
            raise ErrorResponse(**self._error_attributes(100))
        elif list(filter(lambda user_comic: user_comic.get('id') == comic_id, user_comics)):
            self._create_measurement(
                'layaway', f'{username} has this comic {comic_id}', 'Error conflict', method_name)
            raise ErrorResponse(**self._error_attributes(1600))

        was_inserted = self.__db_service.insert_comic_to_link(user_id, comic)
        if was_inserted is None or was_inserted < 1:
            self._create_measurement(
                'MongoDB', 'Failed to insert comic in Mongo', 'Mongo is not up or query bad', method_name)
            raise ErrorResponse(**self._error_attributes(100))

        return f'El usuario {username} tiene el comic {comic_id} en su apartado'

    def _validate_token(self, token: str) -> dict:
        url = self.settings.URL_LOGIN_KEY
        coroutine = self._general_request.get(url=url, headers={
            'authorization': f'Bearer {token}'})
        response = asyncio.run(coroutine)

        if not response['response']:
            if response['type_error'] == 'timeout':
                raise ErrorResponse(**self._error_attributes(103))
            raise ErrorResponse(**self._error_attributes(102))

        if response['status'] == 401:
            details = response['response']['meta'].get('details')
            raise ErrorResponse(**self._error_attributes(104), details=details)

        return response['response']['data']['payload']

    def _get_comic_to_link(self, comic_id: int) -> dict:
        url = f'{self.settings.URL_GET_COMIC_BY_ID}/{comic_id}'
        coroutine = self._general_request.get(url=url)
        response = asyncio.run(coroutine)

        if not response['response']:
            if response['type_error'] == 'timeout':
                raise ErrorResponse(**self._error_attributes(103))
            raise ErrorResponse(**self._error_attributes(102))

        if response['status'] == 404:
            details = ['comic does not exit']
            raise ErrorResponse(**self._error_attributes(107), details=details)

        return response['response']['data']['comic']

    def _create_measurement(self, service: str, message: str, error: str, method_name: str) -> None:
        init_time = time.perf_counter()
        total_time_elapsed = Utils.get_time_elapsed_ms(init_time)
        measurement = Measurement(service, total_time_elapsed, 'error')
        self._log.error(message, method=method_name,
                        error=error, measurement=measurement)

    def _set_logs(self):
        self._log.tracing_id = self.transaction_id
        self._log_external = copy.copy(self._log)
        self._log_external.log_origin = 'EXTERNAL'
        self.__db_service.log = self._log_external
        self._general_request.log = self._log_external
