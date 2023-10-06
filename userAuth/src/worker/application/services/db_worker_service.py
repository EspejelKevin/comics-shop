from worker.domain import DBRepository


class DBWorkerService(DBRepository):

    def __init__(self, db_worker_repository: DBRepository) -> None:
        self.__db_repository = db_worker_repository
        self.log = None

    def is_up(self) -> bool:
        return self.__db_repository.is_up(self.log)

    def get_error_details(self) -> dict:
        return self.__db_repository.get_error_details(self.log)

    def get_user(self, username: str) -> dict:
        return self.__db_repository.get_user(self.log, username)

    def create_user(self, user_data: dict) -> dict:
        return self.__db_repository.create_user(self.log, user_data)
