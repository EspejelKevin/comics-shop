import autodynatrace
import container
from shared.infrastructure import WorkerResponse
from worker.application import (ReadinessUsecase, SignupUsecase,
                                UpdateCacheUsecase)
from worker.domain import UserInput


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
    @autodynatrace.trace('WorkerController - signup')
    def signup(user: UserInput):
        with container.SingletonContainer.scope() as app:
            use_case: SignupUsecase = app.use_cases.signup()
            data = use_case.execute(user)
            return WorkerResponse(content=data)
