from asyncio import Queue
from dataclasses import dataclass


@dataclass
class Queues:
    send_achievements: Queue
