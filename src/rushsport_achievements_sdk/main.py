import asyncio
import logging
from typing import List

from aiohttp import ClientSession

from .dataclasses import Queues
from .choices import TriggerTypes


class AchievementsSDK:
    def __init__(self, achievements_host: str, workers: int):
        self.__logger = logging.getLogger(__name__)
        self.__host = achievements_host
        self.__queues = Queues(send_achievements=asyncio.Queue())
        self.__tasks = []
        self.__workers = workers
        for i in range(workers):
            task = asyncio.create_task(self.__send_achievements_data(i))
            self.__tasks.append(task)

    async def __send_achievements_data(self, number):
        while True:
            async with ClientSession() as session:
                data: dict = await self.__queues.send_achievements.get()
                if not data:
                    self.__logger.info(f"Task {number} was done!")
                    return
                try:
                    await session.post(f'http://{self.__host}/api/achievements/',
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

    async def send_user_won_in_a_row_achievement(self, market_id: int):
        await self.__queues.send_achievements.put({
            'market_id': market_id,
            'trigger_type': TriggerTypes.USER_WON_IN_A_ROW
        })

    async def send_quarter_clock_achievement(self, event_id: int, quarter: int, clock: str):
        await self.__queues.send_achievements.put({
            'event_id': event_id,
            'quarter': quarter,
            'clock': clock,
            'trigger_type': TriggerTypes.QUARTER_CLOCK
        })

    async def close(self):
        async def check_shutdown_tasks(tasks: List[asyncio.Task]):
            for task in tasks:
                if task.done():
                    self.__tasks.remove(task)
                    return
            await asyncio.sleep(1)
            await check_shutdown_tasks(tasks=tasks)

        for i in range(self.__workers):
            await self.__queues.send_achievements.put(None)
            await check_shutdown_tasks(tasks=self.__tasks)
