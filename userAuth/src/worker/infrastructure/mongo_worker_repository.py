import time

from shared.infrastructure import CachedConfig, Log, Measurement, get_settings
from shared.utils import Utils
from worker.domain import DBRepository

settings = get_settings()


class MongoWorkerRepository(DBRepository):

    def __init__(self, session_factory):
        self.session_factory = session_factory
        self.document_error = 'Without the document or it has a bad structure.'

    def is_up(self, log: Log) -> bool:
        with self.session_factory() as session:

            init_time = time.perf_counter()

            data: dict = session.is_up()
            success = data.get('status')
            message = data.get('message')
            method_name = data.get('method')

            time_elapsed = Utils.get_time_elapsed_ms(init_time)

            if success:
                measurement = Measurement('MongoDB', time_elapsed)
                log.info('MongoDB is up', measurement=measurement)
            else:
                measurement = Measurement('MongoDB', time_elapsed, 'Error')
                log.error('MongoDB is not up', method=method_name,
                          error=message, measurement=measurement)
            return success

    @CachedConfig()
    def get_error_details(self, log: Log) -> dict:
        method_name = Utils.get_method_name(self, 'get_error_details')
        init_time = time.perf_counter()

        with self.session_factory() as session:
            db = session.get_db(db_name=settings.MONGO_DB_NAME)
            collection = db.configuraciones
            document_id = {'_id': settings.MONGO_ID_ERROR_DETAILS}
            results = collection.find_one(document_id)

            time_elapsed = Utils.get_time_elapsed_ms(init_time)

            if not results or not results.get('errors'):
                measurement = Measurement('MongoDB', time_elapsed)
                log.error(f'Mongo: Get List of Error Details {settings.MONGO_DB_NAME} {settings.MONGO_URI}',
                          method=method_name, error=self.document_error,
                          object=document_id, measurement=measurement)
                return {}

            measurement = Measurement('MongoDB', time_elapsed)
            log.info('Mongo: Get List of Error Details',
                     measurement=measurement, object=document_id)

            return results['errors']

    def get_user(self, log, username: str) -> dict:
        init_time = time.perf_counter()

        with self.session_factory() as session:
            db = session.get_db(db_name=settings.MONGO_DB_NAME)
            collection = db.users
            query = {'username': username}
            result = collection.find_one(query)

            time_elapsed = Utils.get_time_elapsed_ms(init_time)

            measurement = Measurement('MongoDB', time_elapsed)
            log.info('Mongo: Get user',
                     measurement=measurement, object=query)

            return result if result else {}

    def create_user(self, log, user_data: dict) -> dict:
        init_time = time.perf_counter()

        with self.session_factory() as session:
            db = session.get_db(db_name=settings.MONGO_DB_NAME)
            collection = db.users
            result = collection.insert_one(user_data)

            time_elapsed = Utils.get_time_elapsed_ms(init_time)

            measurement = Measurement('MongoDB', time_elapsed)
            log.info('Mongo: Create user',
                     measurement=measurement)

            return result
