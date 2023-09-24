from enum import Enum


class Frequency(Enum):
    DAILY = 1
    WEEKLY = 2
    BI_WEEKLY = 3
    MONTHLY = 4
    QUARTERLY = 5
    YEARLY = 6
    CUSTOM = 7


class DayOfWeek(Enum):
    MONDAY = 0
    TUESDAY = 1
    WEDNESDAY = 2
    THURSDAY = 3
    FRIDAY = 4
    SATURDAY = 5
    SUNDAY = 6

    @staticmethod
    def from_string(text: str, default):
        for day in DayOfWeek:
            if text == day.name:
                return day
        return default
