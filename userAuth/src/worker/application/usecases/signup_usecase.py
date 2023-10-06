import copy
import time
import uuid

from shared.domain import Response, SuccessResponse
from shared.infrastructure import ErrorResponse, Log, Measurement, Settings
from shared.utils import Utils
from worker.application import Functionalities
from worker.domain import DBRepository, UserRegistration


class SignupUsecase(Functionalities):
    def __init__(self, db_worker_service: DBRepository, log: Log,
                 settings: Settings) -> None:
        self.__db_service = db_worker_service
        self._log = log
        self.settings = settings
        self.transaction_id = str(uuid.uuid4())

    def execute(self, user: UserRegistration) -> Response:
        init_time = time.perf_counter()
        self._set_logs()

        user.id = user.id.hex
        self._log.info('Start: Signup Usecase',
                       object=user.dict(exclude={'password'}))

        self._set_configs(self.__db_service)
        self._get_response(user)

        time_elapsed = Utils.get_time_elapsed_ms(init_time)
        self._log.info('Signup: successfully')

        data = {'message': f'Usuario {user.username} creado con éxito'}
        return SuccessResponse(data, 200, self.transaction_id, time_elapsed)

    def _get_response(self, user: UserRegistration) -> None:
        method_name = Utils.get_method_name(self, '_get_response')
        existing_user = self.__db_service.get_user(user.username)

        if existing_user is None:
            self._create_measurement(
                'MongoDB', 'Failed to get user from Mongo', 'Mongo is not up', method_name)
            raise ErrorResponse(**self._error_attributes(100))

        elif existing_user:
            self._create_measurement(
                '/signup', 'Failed to create user', 'User already exists', method_name)
            raise ErrorResponse(**self._error_attributes(1500))

        user.password = Utils.hash_password(user.password)
        was_inserted = self.__db_service.create_user(user.dict())

        if was_inserted is None:
            self._create_measurement(
                'MongoDB', 'Failed to create user', 'Mongo is not up', method_name)
            raise ErrorResponse(**self._error_attributes(100))

    def _create_measurement(self, service: str, message: str, error: str, method_name: str) -> None:
        init_time = time.perf_counter()
        total_time_elapsed = Utils.get_time_elapsed_ms(init_time)
        measurement = Measurement(service, total_time_elapsed, 'error')
        self._log.error(message, method=method_name,
                        error=error, measurement=measurement)

    def _set_logs(self) -> None:
        self._log.tracing_id = self.transaction_id
        self._log_external = copy.copy(self._log)
        self._log_external.log_origin = 'EXTERNAL'
        self.__db_service.log = self._log_external
