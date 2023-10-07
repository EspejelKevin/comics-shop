import copy
import time
import uuid

from shared.domain import Response, SuccessResponse
from shared.infrastructure import ErrorResponse, Log, Measurement, Settings
from shared.utils import Utils
from worker.application import Functionalities
from worker.domain import DBRepository, SecuritySchema, UserLogin


class LoginUsecase(Functionalities):
    def __init__(self, db_worker_service: DBRepository, log: Log,
                 settings: Settings) -> None:
        self.__db_service = db_worker_service
        self._log = log
        self._security_schema = SecuritySchema()
        self.settings = settings
        self.transaction_id = str(uuid.uuid4())

    def execute(self, user: UserLogin) -> Response:
        init_time = time.perf_counter()
        self._set_logs()

        self._log.info('Start: Login Usecase',
                       object=user.dict(exclude={'password'}))

        self._set_configs(self.__db_service)
        token = self._get_response(user)

        time_elapsed = Utils.get_time_elapsed_ms(init_time)
        self._log.info('Login: successfully')

        response = {
            'message': f'Usuario {user.username} logueado con éxito',
            'token': token
        }
        return SuccessResponse(response, 200, self.transaction_id, time_elapsed)

    def _get_response(self, user: UserLogin) -> str:
        method_name = Utils.get_method_name(self, '_get_response')
        existing_user = self.__db_service.get_user(user.username)

        if existing_user is None:
            self._create_measurement(
                'MongoDB', 'Failed to get user from Mongo', 'Mongo is not up', method_name)
            raise ErrorResponse(**self._error_attributes(100))

        elif not existing_user:
            self._create_measurement(
                '/signup', 'Failed to verify user', 'User does not exist', method_name)
            details = ['user does not exist']
            raise ErrorResponse(**self._error_attributes(107), details=details)

        if not Utils.verify_password(user.password, existing_user.get('password')):
            self._create_measurement(
                '/signup', 'Failed to verify user', 'Password invalid', method_name)
            raise ErrorResponse(**self._error_attributes(1501))

        existing_user.pop('_id')
        token = self._security_schema.create_access_token(existing_user)

        return token

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
