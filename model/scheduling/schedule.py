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
