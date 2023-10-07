from abc import ABCMeta, abstractmethod


class DBRepository(metaclass=ABCMeta):

    @abstractmethod
    def is_up(self, log) -> bool:
        raise NotImplementedError

    @abstractmethod
    def get_error_details(self, log) -> dict:
        raise NotImplementedError

    @abstractmethod
    def insert_comic_to_link(self, log, user_id: str, comic: dict) -> bool:
        raise NotImplementedError

    @abstractmethod
    def get_user_comics(self, log, user_id: str) -> list:
        raise NotImplementedError
