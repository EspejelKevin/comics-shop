import asyncio
import time

from aiohttp import ClientResponse
from aiohttp.client_exceptions import ClientConnectorError, ContentTypeError
from shared.infrastructure.logs.log import Log
from shared.utils import Utils

from .logs.measurement import Measurement
from .session import GeneralSession


class GeneralRequestServer:

    def __init__(self) -> None:
        self.headers = {'Content-Type': 'application/json',
                        'Connection': 'keep-alive'}
        self.init_time = 0
        self.log: Log = None
        self._session = GeneralSession()
        self.error_msg = {'content': "Error al obtener el JSON de la respuesta",
                          'timeout': "Ocurrió un Timeout",
                          'client': "Client Connector Error",
                          'general': "Error al consumir recurso externo",
                          'no_data': "No se obtuvo respuesta en la petición"}

    async def get(self, url: str, query_params: dict = {}, headers: dict = {}) -> dict:
        self.init_time = time.perf_counter()
        headers = {**headers, **self.headers}
        try:
            async with await self._session.client() as session:
                async with session.get(url, params=query_params, headers=headers) as response:
                    return await self._obtain_response(response, 'GET', query_params)
        except Exception as error:
            return self._catched_error(error, url, 'GET', query_params)

    @staticmethod
    def _response(response, status=200, success=False, type_error='', additionals={}) -> dict:
        return {'response': response,
                'status': status,
                'success': success,
                'type_error': type_error,
                'additionals': additionals}

    def _catched_error(self, error: str, url: str, method: str, object_: dict) -> dict:
        match error:
            case error if isinstance(error, asyncio.TimeoutError):
                self._log_error(
                    url, self.error_msg['timeout'], error, method, object_)
                response = self._response(
                    {}, 408, type_error='timeout', additionals={'error': str(error)})
            case error if isinstance(error, ClientConnectorError):
                self._log_error(
                    url, self.error_msg['client'], error, method, object_)
                response = self._response(
                    {}, 500, type_error='clientConnector', additionals={'error': str(error)})
            case _:
                self._log_error(
                    url, self.error_msg['general'], error, method, object_)
                response = self._response(
                    {}, 500, type_error='general', additionals={'error': str(error)})
        return response

    async def _obtain_response(self, response: ClientResponse, method: str,
                               query_params: dict, body: dict = {}) -> dict:
        time_elapsed = Utils.get_time_elapsed_ms(self.init_time)
        URL = response.url.human_repr()
        status = response.status
        adds = {'url': URL, 'time_elapsed': time_elapsed}
        object_ = {'status': status, 'params': query_params}
        try:
            json_data = await response.json()
        except ContentTypeError as error:
            object_.update({'response': await response.text()})
            object_.update({'body': body} if body else body)
            self._log_error(URL, self.error_msg['content'],
                            error, method, object_)
            adds = {'error': str(error), **object_}
            return self._response({}, status, type_error='content_type',
                                  additionals=adds)
        if not response.ok:
            if not json_data:
                json_data = {}
                object_.update({'body': body} if body else body)
                self._log_error(URL, self.error_msg['no_data'],
                                method=method, object=object_)
            adds.update({'body': body} if body else body)
            adds.update({'params': query_params, 'reason': response.reason})
            return self._response(json_data, status, additionals=adds)
        return self._response(json_data, status, True, additionals=adds)

    def _log_error(self, url: str, error_msg: str, error: str | Exception = '',
                   method: str = 'GET', object: dict = None) -> None:
        time_elapsed = Utils.get_time_elapsed_ms(self.init_time)
        method_name = Utils.get_method_name(self, method.lower())
        measurement = Measurement(f"{method}: {url}", time_elapsed, 'Error')
        self.log.error(error_msg, method_name, error, object, measurement)
