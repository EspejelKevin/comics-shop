import time

import autodynatrace
from shared.infrastructure import ErrorResponse, Measurement
from shared.utils import Utils

from .services.db_worker_service import DBWorkerService


class Functionalities:
    @autodynatrace.trace('Functionalities - _set_configs')
    def _set_configs(self, db_service: DBWorkerService) -> None:
        method_name = Utils.get_method_name(self, '_set_configs')
        init_time = time.perf_counter()

        self.db_error_details = db_service.get_error_details()

        if not self.db_error_details:
            time_elapsed = Utils.get_time_elapsed_ms(init_time)
            measurement = Measurement('MongoDB', time_elapsed, 'Error')
            self._log_external.error("Error al conectar con Mongo",
                                     error="Ha ocurrido un error al conectar con Mongo",
                                     method=method_name, measurement=measurement)
            raise ErrorResponse(error_code=100, message="Error de conexión a mongo.",
                                transaction_id=self.transaction_id, status_code=500,
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
