from abc import ABC, abstractmethod
from collections import namedtuple
import random
import pendulum

server_reset = 10

ReminderEvent = namedtuple("ReminderEvent", ["type", "datetime", "title", "detail", "message"])

class Scheduler(ABC):
    """Base for E7 event reminder schedule providers"""

    @abstractmethod
    def next_datetime (self) -> pendulum.DateTime:
        """Returns the next event datetime"""
        pass

    @abstractmethod
    def next (self) -> ReminderEvent:
        """Returns the next event"""
        pass

    def description (self) -> str:
        """Returns the scheduler description"""
        return self.__doc__

# Schedulers -----------------------------------------

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

    def next_datetime (self):
        now = pendulum.now('UTC')
        weekday = now.weekday() + 1
        if weekday in self.gw_weekdays and now < now.at(server_reset):
            return now.at(server_reset)
        else:
            next_weekday = min(filter(lambda x: x > weekday, self.gw_weekdays), default=pendulum.MONDAY)
            return now.next(next_weekday).at(server_reset)

    def next (self):
        dt = self.next_datetime()
        weekday = dt.weekday() + 1
        meta = self.events[weekday]
        return ReminderEvent(
            self.type, 
            dt, 
            meta[0], 
            meta[1], 
            self._generate_message(meta[0])
        )

class LOL(Scheduler):
    """Just for testing"""
    type = 'lol'

    def next_datetime (self):
        return pendulum.now().add(seconds=5)

    def next (self):
        return ReminderEvent(self.type, self.next_datetime(), 'KEK', 'hi', 'You have been kekd')

# ----------------------------------------------------

class Reminders:
    types = {
        GWScheduler
    }

    def __init__ (self):
        self.schedulers = {s.type: s() for s in self.types}

    def next_event (self):
        """Returns the nearest event"""
        return min([s.next() for s in self.schedulers.values()], key=lambda e: e.datetime)