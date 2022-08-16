import asyncio

import aiohttp

from .dataclasses import Queues


class AchievementsSDK:
    def __init__(self, app, logger, db_pool):
        self.logger = logger
        self.app = app
        self.host = app.config.ACHIEVEMENT_SERVICE_HOST
        self.aio_session = aiohttp.ClientSession()
        self.db_pool = db_pool
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
                continue

    async def send_achievement(self, achievements_data):
        await self.queues.send_achievements.put(achievements_data)
