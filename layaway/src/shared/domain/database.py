from abc import abstractmethod
from contextlib import contextmanager


class Session:
    pass


class Database:
    @abstractmethod
    @contextmanager
    def session(self): pass
