from worker.domain import DBRepository


class DBWorkerService(DBRepository):

    def __init__(self, db_worker_repository: DBRepository) -> None:
        self.__db_repository = db_worker_repository
        self.log = None

    def is_up(self) -> bool:
        return self.__db_repository.is_alive(self.log)

    def get_error_details(self) -> dict:
        return self.__db_repository.get_error_details(self.log)
