from abc import ABC, abstractmethod
from collections import namedtuple
import pendulum

ReminderEvent = namedtuple("ReminderEvent", ["type", "datetime", "timediff", "title", "detail", "message"])

class Scheduler(ABC):
    """Base for E7 event reminder schedule providers"""
    def __init__ (self, priority):
        self.priority = priority * 5

    @abstractmethod
    async def next_datetime (self) -> pendulum.DateTime:
        """Returns the next event datetime"""

    @abstractmethod
    async def next (self) -> ReminderEvent:
        """Returns the next event"""

    def description (self) -> str:
        """Returns the scheduler description"""
        return self.__doc__
