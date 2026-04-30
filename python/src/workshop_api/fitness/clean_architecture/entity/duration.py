from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class Duration:
    start_date: date
    end_date: date

    def in_months(self) -> int:
        months = (self.end_date.year - self.start_date.year) * 12
        months += self.end_date.month - self.start_date.month

        if self.end_date.day < self.start_date.day:
            months -= 1

        return months
