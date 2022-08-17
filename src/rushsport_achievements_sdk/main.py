import asyncio

from .dataclasses import Queues
from .choices import TriggerTypes


class AchievementsSDK:
    def __init__(self, achievements_host, aio_session, logger):
        self.logger = logger
        self.host = achievements_host
        self.aio_session = aio_session
        self.queues = Queues(send_achievements=asyncio.Queue())
        asyncio.create_task(self.__send_achievements_data())

    async def __send_achievements_data(self):
        while True:
            data: dict = await self.queues.send_achievements.get()
            try:
                await self.aio_session.post(f'http://{self.host}/api/achievements/',
                                            json=data, ssl=False)
            except Exception as e:
                self.logger.exception(f'Problem send_achievements_data. Exception: {e}')

    async def send_user_plays_market_achievement(self, user_id: int, team_id: int, event_id: int, value: int = None):
        await self.queues.send_achievements.put({
            'user_id': user_id,
            'team_id': team_id,
            'event_id': event_id,
            'value': value,
            'trigger_type': TriggerTypes.USER_PLAYS_MARKETS
        })
