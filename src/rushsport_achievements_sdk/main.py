import asyncio
import logging

from aiohttp import ClientSession

from .dataclasses import Queues
from .choices import TriggerTypes


class AchievementsSDK:
    def __init__(self, achievements_host: str, aio_session: ClientSession, workers: int):
        self.__logger = logging.getLogger(__name__)
        self.__host = achievements_host
        self.__aio_session = aio_session
        self.__queues = Queues(send_achievements=asyncio.Queue())
        for _ in range(workers):
            asyncio.create_task(self.__send_achievements_data())

    async def __send_achievements_data(self):
        while True:
            data: dict = await self.__queues.send_achievements.get()
            try:
                await self.__aio_session.post(f'http://{self.__host}/api/achievements/',
                                              json=data, ssl=False)
            except Exception as e:
                self.__logger.exception(f'Problem send_achievements_data. Exception: {e}')

    async def send_user_plays_market_achievement(self, user_id: int, team_id: int, event_id: int, value: int = None):
        await self.__queues.send_achievements.put({
            'user_id': user_id,
            'team_id': team_id,
            'event_id': event_id,
            'value': value,
            'trigger_type': TriggerTypes.USER_PLAYS_MARKETS
        })
