from aiohttp import ClientSession, ClientTimeout, TCPConnector

from .settings import get_settings

settings = get_settings()


class GeneralSession:
    async def client(self) -> ClientSession:
        session: ClientSession = ClientSession(
            timeout=ClientTimeout(total=settings.HTTP_TIMEOUT_SEC),
            connector=TCPConnector(ssl=True, limit=3))
        return session
