import time

from passlib.context import CryptContext
from passlib.hash import des_crypt, md5_crypt, sha256_crypt

crypt_context = CryptContext([sha256_crypt, md5_crypt, des_crypt])


class Utils:
    @staticmethod
    def get_method_name(obj, func_name: str = '') -> str:
        obj_class_name = f'{obj.__class__.__module__}.{obj.__class__.__qualname__}'
        full_name = obj_class_name + '.' + func_name if func_name else obj_class_name
        return full_name

    @staticmethod
    def add_attributes(obj, data: dict) -> None:
        for key, value in data.items():
            setattr(obj, key, value)

    @staticmethod
    def discard_empty_attributes(obj) -> None:
        obj_copy = obj.__dict__.copy()
        for key, value in obj_copy.items():
            if not value:
                delattr(obj, key)

    @staticmethod
    def sort_attributes(obj) -> None:
        obj.__dict__ = dict(sorted(obj.__dict__.items()))

    @staticmethod
    def get_time_elapsed_ms(init_time: float, decimals: int = 2):
        current_time = time.perf_counter()
        time_elapsed = current_time - init_time
        return round(time_elapsed * 1000, decimals)

    @staticmethod
    def get_error_details(errors):
        return list(map(lambda error:
                        f"{error['loc'][1]}: {error['msg']} in {error['loc'][0]}"
                        if len(error['loc']) > 1 else f"{error['loc'][0]}: required", errors))

    @staticmethod
    def get_error_details_query_params(errors: dict) -> list:
        details = list(map(
            lambda error: f"{error['loc'][0]}: {error['msg']} in {error['loc'][1]}", errors))
        return details

    @staticmethod
    def hash_password(password: str) -> str:
        hashed_password = crypt_context.hash(password)
        return hashed_password

    @staticmethod
    def verify_password(password: str, hashed_password: str) -> bool:
        return crypt_context.verify(password, hashed_password)
