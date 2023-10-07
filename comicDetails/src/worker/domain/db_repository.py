from abc import ABCMeta, abstractmethod


class DBRepository(metaclass=ABCMeta):

    @abstractmethod
    def is_up(self, log) -> bool:
        raise NotImplementedError

    @abstractmethod
    def get_error_details(self, log) -> dict:
        raise NotImplementedError
