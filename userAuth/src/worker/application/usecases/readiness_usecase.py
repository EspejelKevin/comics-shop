import copy
import time
import uuid

from shared.domain import Response, SuccessResponse
from shared.infrastructure import ErrorResponse, Log, Settings
from shared.utils import Utils
from worker.application import Functionalities
from worker.domain import DBRepository


class ReadinessUsecase(Functionalities):
    def __init__(self, db_worker_service: DBRepository, log: Log,
                 settings: Settings) -> None:
        self.__db_service = db_worker_service
        self._log = log
        self.settings = settings
        self.transaction_id = str(uuid.uuid4())

    def execute(self) -> Response:
        init_time = time.perf_counter()
        self._set_logs()

        self._log.info('Start: Readiness')

        if not self.__db_service.is_up():
            raise ErrorResponse(error_code=100, message='Error de conexión a mongo.',
                                transaction_id=self.transaction_id, status_code=500,
                                code_name='500.general-error.100')

        time_elapsed = Utils.get_time_elapsed_ms(init_time)

        data = {'status': 'Mongo is up'}
        return SuccessResponse(data, 200, self.transaction_id, time_elapsed)

    def _set_logs(self):
        self._log.tracing_id = self.transaction_id
        self._log_external = copy.copy(self._log)
        self._log_external.log_origin = 'EXTERNAL'
        self.__db_service.log = self._log_external
