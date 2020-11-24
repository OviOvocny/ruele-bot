import asyncio

from modules.schedulers.gw import GWScheduler
from modules.schedulers.hall import HallScheduler
from modules.schedulers.streams import LiveStreamScheduler

class Reminders:
    # schedulers to init and use, same time events will fire in order specified
    types = [
        GWScheduler,
        HallScheduler,
        LiveStreamScheduler
    ]

    def __init__ (self):
        self.schedulers = {s.type: s(i) for i, s in enumerate(self.types)}

    async def upcoming (self):
        """Returns the nearest event"""
        event_list = await asyncio.gather(*[s.next() for s in self.schedulers.values()])
        while None in event_list:
            event_list.remove(None)
        return sorted(event_list, key=lambda e: e.datetime)
