from abc import ABCMeta, abstractmethod


class DBRepository(metaclass=ABCMeta):

    @abstractmethod
    def is_up(self, log) -> bool:
        raise NotImplementedError

    @abstractmethod
    def get_error_details(self, log) -> dict:
        raise NotImplementedError

    @abstractmethod
    def get_user(self, log, username: str) -> dict:
        raise NotImplementedError

    @abstractmethod
    def create_user(self, log, user_data: dict) -> dict:
        raise NotImplementedError
