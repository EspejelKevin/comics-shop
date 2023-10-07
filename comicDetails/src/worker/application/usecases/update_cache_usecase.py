import copy
import time
import uuid

from shared.infrastructure import Log, Measurement, Settings
from shared.utils import Utils
from worker.application import Functionalities
from worker.domain import DBRepository


class UpdateCacheUsecase(Functionalities):
    def __init__(self, db_worker_service: DBRepository, log: Log,
                 settings: Settings) -> None:
        self.__db_service = db_worker_service
        self._log = log
        self.settings = settings
        self.transaction_id = str(uuid.uuid4())

    def execute(self) -> None:
        init_time = time.perf_counter()
        self._set_logs()

        self._log.info('Start: Update Cache')

        self._set_configs(self.__db_service)

        time_elapsed = Utils.get_time_elapsed_ms(init_time)
        measurement = Measurement('MongoDB', time_elapsed)
        self._log.info('Set settings in cache: Success',
                       measurement=measurement)

    def _set_logs(self):
        self._log.tracing_id = self.transaction_id
        self._log_external = copy.copy(self._log)
        self._log_external.log_origin = 'EXTERNAL'
        self.__db_service.log = self._log_external
