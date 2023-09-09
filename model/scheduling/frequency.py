from enum import Enum


class Frequency(Enum):
    DAILY = 1
    WEEKLY = 2
    BI_WEEKLY = 3
    MONTHLY = 4
    YEARLY = 5
    CUSTOM = 6


class DayOfWeek(Enum):
    MONDAY = 0
    TUESDAY = 1
    WEDNESDAY = 2
    THURSDAY = 3
    FRIDAY = 4
    SATURDAY = 5
    SUNDAY = 6
