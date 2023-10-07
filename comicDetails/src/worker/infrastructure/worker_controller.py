import autodynatrace
import container
from shared.infrastructure import WorkerResponse
from worker.application import (GetRecordsUsecase, GetRecordUsecase,
                                ReadinessUsecase, UpdateCacheUsecase)
from worker.domain import Filter


class WorkerController:
    @staticmethod
    @autodynatrace.trace('WorkerController - readiness')
    def readiness():
        with container.SingletonContainer.scope() as app:
            use_case: ReadinessUsecase = app.use_cases.readiness()
            data = use_case.execute()
            return WorkerResponse(content=data)

    @staticmethod
    @autodynatrace.trace('WorkerController - update_cache')
    def update_cache():
        with container.SingletonContainer.scope() as app:
            use_case: UpdateCacheUsecase = app.use_cases.update_cache()
            use_case.execute()

    @staticmethod
    @autodynatrace.trace('WorkerController - get_records')
    def get_records(filter: Filter):
        with container.SingletonContainer.scope() as app:
            use_case: GetRecordsUsecase = app.use_cases.get_records()
            data = use_case.execute(filter)
            return WorkerResponse(content=data)

    @staticmethod
    @autodynatrace.trace('WorkerController - get_record')
    def get_record(id: int):
        with container.SingletonContainer.scope() as app:
            use_case: GetRecordUsecase = app.use_cases.get_record()
            data = use_case.execute(id)
            return WorkerResponse(content=data)
