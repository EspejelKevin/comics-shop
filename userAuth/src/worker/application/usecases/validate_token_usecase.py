import copy
import json
import time
import uuid

from jose import ExpiredSignatureError, JWSError
from shared.domain import Response, SuccessResponse
from shared.infrastructure import ErrorResponse, Log, Measurement, Settings
from shared.utils import Utils
from worker.application import Functionalities
from worker.domain import DBRepository, SecuritySchema


class ValidateTokenUsecase(Functionalities):
    def __init__(self, db_worker_service: DBRepository, log: Log,
                 settings: Settings) -> None:
        self.__db_service = db_worker_service
        self._log = log
        self._security_schema = SecuritySchema()
        self.settings = settings
        self.transaction_id = str(uuid.uuid4())

    def execute(self, token: str) -> Response:
        init_time = time.perf_counter()
        self._set_logs()

        self._log.info('Start: Validate Token Usecase',
                       object={'token': token})

        self._set_configs(self.__db_service)
        payload = self._get_response(token)

        time_elapsed = Utils.get_time_elapsed_ms(init_time)
        self._log.info('Validate token: successfully')

        data = {
            'message': 'Token válido',
            'payload': payload
        }
        return SuccessResponse(data, 200, self.transaction_id, time_elapsed)

    def _get_response(self, token) -> dict:
        method_name = Utils.get_method_name(self, '_get_response')

        try:
            unauthorized_exception = ErrorResponse(
                **self._error_attributes(104))
            payload = json.loads(
                self._security_schema.decode_access_token(token))
            user = payload['sub']
            if not user:
                self._create_measurement(
                    'JWT', 'Without payload', 'User does not exist', method_name)
                raise unauthorized_exception

            user.pop('password')
            user.pop('name')
            user.pop('age')

            return user

        except JWSError as e:
            self._create_measurement(
                'JWT', 'Invalid token', e, method_name)
            unauthorized_exception.meta['details'] = [
                'Token inválido o secret key incorrecta']
            raise unauthorized_exception
        except ExpiredSignatureError as e:
            self._create_measurement(
                'JWT', 'Expired token', e, method_name)
            unauthorized_exception.meta['details'] = ['El token ha expirado']
            raise unauthorized_exception
        except Exception as e:
            self._create_measurement(
                'JWT', 'Error general', e, method_name)
            unauthorized_exception.meta['details'] = [
                'No fue posible decodificar el token']
            raise unauthorized_exception

    def _create_measurement(self, service: str, message: str, error: str | Exception, method_name: str) -> None:
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
