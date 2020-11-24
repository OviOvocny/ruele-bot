import pendulum

from modules.schedulers.base import Scheduler, ReminderEvent
from modules.utils import timediff
from constants import SERVER_RESET

practice_desc = "Practice battles let you try out team compositions and strategies before the challenge."
challenge_desc = "Place in Hall of Trials ranking and get currency for exclusive equipment and more."

class HallScheduler(Scheduler):
    """Event reminders for Hall of Trials resets"""
    type = 'hall of trials'

    seed_dt = pendulum.datetime(2020,11,23,10, tz='UTC')

    events = [
        (
            "Zeno (Practice) in Hall of Trials",
            practice_desc
        ),
        (
            "Zeno in Hall of Trials",
            challenge_desc
        ),
        (
            "Kayron (Practice) in Hall of Trials",
            practice_desc
        ),
        (
            "Kayron in Hall of Trials",
            challenge_desc
        ),
        (
            "Nilgal (Practice) in Hall of Trials",
            practice_desc
        ),
        (
            "Nilgal in Hall of Trials",
            challenge_desc
        ),
        (
            "Archdemon Mercedes (Practice) in Hall of Trials",
            practice_desc
        ),
        (
            "Archdemon Mercedes in Hall of Trials",
            challenge_desc
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
            f'you can now battle {meta[0]}! Good luck.'
        )
