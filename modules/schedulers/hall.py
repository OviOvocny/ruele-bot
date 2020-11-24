import pendulum

from modules.schedulers.base import Scheduler, ReminderEvent
from modules.utils import timediff
from constants import SERVER_RESET

class HallScheduler(Scheduler):
    """Event reminders for Hall of Trials resets"""
    type = 'hall of trials'

    seed_dt = pendulum.datetime(2020,11,23,10, tz='UTC')

    events = [
        (
            "Zeno (Practice) in Hall of Trials",
            "."
        ),
        (
            "Zeno in Hall of Trials",
            "."
        ),
        (
            "Kayron (Practice) in Hall of Trials",
            "."
        ),
        (
            "Kayron in Hall of Trials",
            "."
        ),
        (
            "Nilgal (Practice) in Hall of Trials",
            "."
        ),
        (
            "Nilgal in Hall of Trials",
            "."
        ),
        (
            "Archdemon Mercedes (Practice) in Hall of Trials",
            "."
        ),
        (
            "Archdemon Mercedes in Hall of Trials",
            "."
        ),
    ]

    def next_datetime (self):
        now = pendulum.now('UTC')
        weekday = now.weekday() + 1
        if weekday == pendulum.MONDAY and now < now.at(SERVER_RESET):
            return now.at(SERVER_RESET, 0, self.priority)
        else:
            return now.next(pendulum.MONDAY).at(SERVER_RESET, 0, self.priority)

    def next (self):
        dt = self.next_datetime()
        week_seed_diff = self.seed_dt.diff(dt).in_weeks()
        meta = self.events[week_seed_diff % len(self.events)]
        return ReminderEvent(
            self.type, 
            dt, 
            timediff(dt),
            meta[0], 
            meta[1], 
            f'you can now battle {meta[0]}'
        )
