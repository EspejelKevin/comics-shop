import autodynatrace
import container
from shared.infrastructure import WorkerResponse
from worker.application import (GetRelatedComicsUsecase, ReadinessUsecase,
                                RelatedComicsUsecase, UpdateCacheUsecase)
from worker.domain import ComicInput, Filter


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
    @autodynatrace.trace('WorkerController - related_comics')
    def related_comics(comic_input: ComicInput, token: str):
        with container.SingletonContainer.scope() as app:
            use_case: RelatedComicsUsecase = app.use_cases.related_comics()
            data = use_case.execute(comic_input, token)
            return WorkerResponse(content=data)

    @staticmethod
    @autodynatrace.trace('WorkerController - get_related_comics')
    def get_related_comics(filter: Filter, token: str):
        with container.SingletonContainer.scope() as app:
            use_case: GetRelatedComicsUsecase = app.use_cases.get_related_comics()
            data = use_case.execute(filter, token)
            return WorkerResponse(content=data)
