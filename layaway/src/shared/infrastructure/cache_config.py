class CachedConfig:
    cached_responses: dict = {}

    def __call__(self, func):
        def get_config_cached(*args, **kwargs):
            full_name = func.__qualname__
            update_cache = kwargs.get('update_cache')
            test = kwargs.get('test')
            is_cached = self.cached_responses.get(full_name) is not None
            if is_cached:
                is_cached = self.cached_responses.get(full_name)[
                    'data'] is not None
            if test:
                del kwargs['test']
                return func(*args, **kwargs)
            if not is_cached or update_cache:
                res = func(*args, **kwargs)
                self.cached_responses[full_name] = {'data': res}
            return self.cached_responses[full_name]['data']

        return get_config_cached

    @classmethod
    def get_cached_responses(cls, func_name: str) -> dict:
        if func_name in cls.cached_responses:
            return cls.cached_responses[func_name]
        return {'data': None}
