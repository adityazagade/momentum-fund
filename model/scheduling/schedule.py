from datetime import date

from model.scheduling.frequency import Frequency, DayOfWeek


class Schedule:
    def __init__(self,
                 start_date: date = None,
                 end_date: date = None,
                 frequency: Frequency = None,
                 interval: int = None,
                 day_of_week: DayOfWeek = None,
                 day_of_month: int = None):
        self.start_date = start_date
        self.end_date = end_date
        self.frequency = frequency
        self.interval = interval
        self.day_of_week = day_of_week
        self.day_of_month = day_of_month

    def matches(self, d: date) -> bool:
        if self.start_date is not None and d < self.start_date:
            return False

        if self.end_date is not None and d > self.end_date:
            return False

        if self.frequency is None:
            return False

        if self.frequency == Frequency.DAILY:
            return True

        if self.frequency == Frequency.WEEKLY:
            if self.day_of_week is None:
                return False
            return d.weekday() == self.day_of_week.value

        if self.frequency == Frequency.BI_WEEKLY:
            if self.day_of_week is None:
                return False
            return d.weekday() == self.day_of_week.value and d.isocalendar()[1] % 2 == 0

        if self.frequency == Frequency.MONTHLY:
            if self.day_of_month is None:
                return False
            return d.day == self.day_of_month

        if self.frequency == Frequency.QUARTERLY:
            if self.day_of_month is None:
                return False
            return d.day == self.day_of_month and d.month in [3, 6, 9, 12]

        if self.frequency == Frequency.YEARLY:
            if self.day_of_month is None:
                return False
            return d.day == self.day_of_month and d.month == 12

        return False
