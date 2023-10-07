import asyncio
import copy
import time
import uuid

import autodynatrace
from shared.domain import Response, SuccessResponse
from shared.infrastructure import (ErrorResponse, GeneralRequestServer, Log,
                                   Settings)
from shared.utils import Utils
from worker.application import Functionalities
from worker.domain import Character, Comic, DBRepository, Filter


class GetRecordsUsecase(Functionalities):

    def __init__(self, db_worker_service: DBRepository,
                 log: Log, settings: Settings) -> None:
        self.__db_service = db_worker_service
        self._log = log
        self._settings = settings
        self._general_request = GeneralRequestServer()
        self.transaction_id = str(uuid.uuid4())
        self.init_time = time.perf_counter()

    @autodynatrace.trace('GetRecordsUseCase - execute')
    def execute(self, filter: Filter) -> Response:
        self._set_logs()
        self._set_configs(self.__db_service)

        params = filter.dict(exclude_none=True)
        self._log.info("Start: /records", object=params)

        data = self._get_records(params)

        total_time_elapsed = Utils.get_time_elapsed_ms(self.init_time)

        self._log.info("Get Records: Success")

        return SuccessResponse(data, 200, self.transaction_id, total_time_elapsed)

    def _get_records(self, params: str):
        title = params.get('comic', '')
        number = params.get('number', 0)
        year = params.get('year', 2023)
        name = params.get('character', '')
        contains = params.get('contains', '')
        page = params.get('page', 0)
        data = {}

        url_comics = self._get_url(page, type_url='comics')
        if title:
            data = {'title': title, 'number': number,
                    'year': year, 'comic': {}}
            url_comics += f'&title={title}&issueNumber={number}&startYear={year}'
            comic_item = self._get_marvel_data(url_comics)
            if comic_item:
                comic_item = comic_item[0]
                comic = Comic.parse_obj({
                    'id': comic_item['id'],
                    'title': comic_item['title'],
                    'image': f"{comic_item['thumbnail']['path']}.{comic_item['thumbnail']['extension']}",
                    'on_sale_date': [obj['date'] for obj in comic_item['dates'] if obj.get('type') == 'onsaleDate'].pop()
                })
                data['comic'] = comic
            return data

        url_characters = self._get_url(page, type_url='characters')
        if name:
            data = {'character': {}}
            url_characters += f'&name={name}'
            character_item = self._get_marvel_data(url_characters)
            if character_item:
                character_item = character_item[0]
                character = Character.parse_obj({
                    'id': character_item['id'],
                    'name': character_item['name'],
                    'image': f"{character_item['thumbnail']['path']}.{character_item['thumbnail']['extension']}",
                    'appearances': character_item['comics']['available']
                })
                data['character'] = character
            return data

        comic_items = []
        comics = []

        if contains:
            url_characters += f'&nameStartsWith={contains}'
            url_comics += f'&titleStartsWith={contains}'
            comic_items = self._get_marvel_data(url_comics)
            comics = [
                Comic.parse_obj({
                    'id': item['id'],
                    'title': item['title'],
                    'image': f"{item['thumbnail']['path']}.{item['thumbnail']['extension']}",
                    'on_sale_date': [obj['date'] for obj in item['dates'] if obj.get('type') == 'onsaleDate'].pop()
                }) for item in comic_items
            ]

        character_items = self._get_marvel_data(url_characters)
        characters = [
            Character.parse_obj({
                'id': item['id'],
                'name': item['name'],
                'image': f"{item['thumbnail']['path']}.{item['thumbnail']['extension']}",
                'appearances': item['comics']['available']
            }) for item in character_items
        ]

        data['page'] = page
        data['count'] = len(characters) + len(comics)

        if contains:
            data['count_comics'] = len(comics)
            data['count_characters'] = len(characters)
            data['comics'] = comics

        data['characters'] = characters

        return data

    # General Request ----------------------------------------------------------

    @autodynatrace.trace('GetRecordsUseCase - _get_marvel_data')
    def _get_marvel_data(self, url: str):
        """ Obtiene los personajes o comics de Marvel por paginación. """
        coroutine = self._general_request.get(url)
        response = asyncio.run(coroutine)

        if not response['response']:
            if response['type_error'] == 'timeout':
                raise ErrorResponse(**self._error_attributes(103))
            raise ErrorResponse(**self._error_attributes(102))

        adds: dict = response['additionals']

        if not response['success']:
            user_message = "Error al consumir el recurso externo"
            self._request_log_error(adds['url'], user_message, adds['time_elapsed'],
                                    adds['reason'], 'GET')
            raise ErrorResponse(**self._error_attributes(102),
                                details=adds['reason'])

        self._request_log_info(adds['url'], "Success getting characters data.",
                               adds['time_elapsed'], 'GET')

        return response['response']['data']['results']

    # General Functions --------------------------------------------------------

    def _set_logs(self):
        self._log.tracing_id = self.transaction_id
        self._log_external = copy.deepcopy(self._log)
        self._log_external.log_origin = 'EXTERNAL'
        self._general_request.log = self._log_external
