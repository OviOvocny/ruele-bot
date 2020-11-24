from modules.schedulers.gw import GWScheduler
from modules.schedulers.hall import HallScheduler

class Reminders:
    # schedulers to init and use, same time events will fire in order specified
    types = [
        GWScheduler,
        HallScheduler
    ]

    def __init__ (self):
        self.schedulers = {s.type: s(i) for i, s in enumerate(self.types)}

    def upcoming (self):
        """Returns the nearest event"""
        return sorted([s.next() for s in self.schedulers.values()], key=lambda e: e.datetime)