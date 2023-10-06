from shared.infrastructure.settings import get_settings

settings = get_settings()

config = {
    'monitorInterval': 10,  # auto reload time interval [secs]
    'loggers': {
        'root': {
            'level': 'INFO',
            'AppenderRef': [settings.APPENDERS]
        }
    },
    'appenders': {
        'console': {
            'type': 'console',
            'target': 'console',
            'PatternLayout': "%(message)s\n"
        }
    }
}
