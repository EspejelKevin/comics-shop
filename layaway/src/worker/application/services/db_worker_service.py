from worker.domain import DBRepository


class DBWorkerService(DBRepository):

    def __init__(self, db_worker_repository: DBRepository) -> None:
        self.__db_repository = db_worker_repository
        self.log = None

    def is_up(self) -> bool:
        return self.__db_repository.is_up(self.log)

    def get_error_details(self) -> dict:
        return self.__db_repository.get_error_details(self.log)

    def insert_comic_to_link(self, user_id: str, comic: dict) -> bool:
        return self.__db_repository.insert_comic_to_link(self.log, user_id, comic)

    def get_user_comics(self, user_id: str) -> list:
        return self.__db_repository.get_user_comics(self.log, user_id)
