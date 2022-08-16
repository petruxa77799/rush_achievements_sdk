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
                async with self.db_pool.acquire() as con:
                    event_achievement = await con.fetchval(
                        """
                        SELECT ea.value
                        FROM eventachievement as ea
                        JOIN achievement ach on ach.id = ea.achievement_id
                        WHERE ea.event_id=$1 AND ach.team_id=$2 AND ea.trigger_type=$3
                        """, data['event_id'], data['team_id'], data['trigger_type'])
                if event_achievement:
                    data['value'] = event_achievement['value']
                    await self.__send_trigger(achievements_data=data)
            except Exception as e:
                self.logger.exception(f'Problem send_achievements_data. Exception: {e}')
                continue

    async def __send_trigger(self, achievements_data):
        try:
            await self.aio_session.post(f'http://{self.host}/api/achievements/',
                                        json=achievements_data, ssl=False)
        except Exception as e:
            self.logger.exception(f'Problem with send trigger to achievements service. Exception: {e}')

    async def send_achievement(self, achievements_data):
        await self.queues.send_achievements.put(achievements_data)
