from datetime import datetime

from shared.utils import Utils


class MetadataResponse:
    def __init__(self, transaction_id: str, time_elapsed: int | float = None, **kwargs) -> None:
        self.transaction_id = transaction_id
        self.timestamp = datetime.now()
        self.time_elapsed = time_elapsed
        Utils.add_attributes(self, kwargs)
        Utils.discard_empty_attributes(self)
        Utils.sort_attributes(self)


class Response:

    data: dict
    meta: MetadataResponse

    def __init__(self, data: dict, meta: MetadataResponse) -> None:
        self.data = data
        self.meta = meta


class SuccessResponse(Response):
    def __init__(self, data: dict, status_code: int, transaction_id: str, time_elapsed: int | float, **kwargs) -> None:
        self._status_code = status_code
        meta = MetadataResponse(transaction_id, time_elapsed, **kwargs)
        super().__init__(data, meta)


class FailureResponse(Response):
    def __init__(self, data: dict, status_code: int, transaction_id: str, **kwargs) -> None:
        self._status_code = status_code
        meta = MetadataResponse(transaction_id, **kwargs)
        super().__init__(data, meta)
