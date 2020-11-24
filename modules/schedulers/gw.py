import random
import pendulum

from modules.schedulers.base import Scheduler, ReminderEvent
from modules.utils import timediff
from constants import SERVER_RESET

class GWScheduler(Scheduler):
    """Event reminders for starts of guild wars"""
    type = 'guild wars'

    gw_weekdays = (pendulum.MONDAY, pendulum.WEDNESDAY, pendulum.FRIDAY)

    events = {
        pendulum.MONDAY: (
            "Monday Guild War",
            "The regular Ezeran mock war between guilds, next on Monday."
        ),
        pendulum.WEDNESDAY: (
            "Wednesday Guild War",
            "The regular Ezeran mock war between guilds, next this Wednesday."
        ),
        pendulum.FRIDAY: (
            "Friday Guild War",
            "The regular Ezeran mock war between guilds, last time this week on Friday."
        )
    }

    messages = [
        "wake up, it's the {title}!",
        "hey! Listen! The {title} just started!",
        "don't forget about the {title}, it's time!",
        "here's your regular reminder to participate in the {title}!",
        "go kick some ass, it's the {title}!"
    ]

    def _generate_message (self, title):
        return random.choice(self.messages).format(title=title)

    def next_datetime (self) -> pendulum.DateTime:
        now = pendulum.now('UTC')
        weekday = now.weekday() + 1
        if weekday in self.gw_weekdays and now < now.at(SERVER_RESET):
            return now.at(SERVER_RESET, 0, self.priority)
        else:
            next_weekday = min(filter(lambda x: x > weekday, self.gw_weekdays), default=pendulum.MONDAY)
            return now.next(next_weekday).at(SERVER_RESET, 0, self.priority)

    def next (self):
        dt = self.next_datetime()
        weekday = dt.weekday() + 1
        meta = self.events[weekday]
        return ReminderEvent(
            self.type, 
            dt, 
            timediff(dt),
            meta[0], 
            meta[1], 
            self._generate_message(meta[0])
        )
