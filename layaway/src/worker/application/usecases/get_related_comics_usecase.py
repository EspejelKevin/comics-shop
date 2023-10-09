import asyncio
import copy
import time
import uuid

from shared.domain import Response, SuccessResponse
from shared.infrastructure import (ErrorResponse, GeneralRequestServer, Log,
                                   Measurement, Settings)
from shared.utils import Utils
from worker.application import Functionalities
from worker.domain import DBRepository, Filter


class GetRelatedComicsUsecase(Functionalities):
    def __init__(self, db_worker_service: DBRepository, log: Log,
                 settings: Settings) -> None:
        self.__db_service = db_worker_service
        self._log = log
        self.settings = settings
        self.transaction_id = str(uuid.uuid4())
        self._general_request = GeneralRequestServer()

    def execute(self, filter: Filter, token: str) -> Response:
        init_time = time.perf_counter()
        self._set_logs()

        self._log.info('Start: Get Related Comics Usecase',
                       object=filter.dict())

        self._set_configs(self.__db_service)

        response = self._get_response(filter, token)

        time_elapsed = Utils.get_time_elapsed_ms(init_time)
        self._log.info('GetRelatedComics: successfully')

        return SuccessResponse(response, 200, self.transaction_id, time_elapsed)

    def _get_response(self, filter: Filter, token: str) -> dict:
        method_name = Utils.get_method_name(self, '_get_response')
        user = self._validate_token(token)
        user_id = user.get('id')
        layaway = {'user_id': user_id, 'comics': []}

        user_comics = self.__db_service.get_user_comics(user_id)

        if user_comics is None:
            self._create_measurement(
                'MongoDB', 'Failed to get comics from Mongo', 'Mongo is not up', method_name)
            raise ErrorResponse(**self._error_attributes(100))
        elif not user_comics:
            return layaway

        if filter.alphabetically:
            user_comics = sorted(user_comics,
                                 key=lambda item: item['title'])
        if filter.date:
            user_comics = sorted(user_comics,
                                 key=lambda item: item['on_sale_date'])

        layaway['comics'] = user_comics

        return layaway

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
