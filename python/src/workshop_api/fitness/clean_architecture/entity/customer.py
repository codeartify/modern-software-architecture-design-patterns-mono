from dataclasses import dataclass
from datetime import date
from uuid import UUID


@dataclass(frozen=True)
class Customer:
    id: UUID
    date_of_birth: date
    email_address: str

    LEGAL_AGE = 18

    def is_underage_at(self, checked_at: date) -> bool:
        age = checked_at.year - self.date_of_birth.year - (
            (checked_at.month, checked_at.day)
            < (self.date_of_birth.month, self.date_of_birth.day)
        )
        return age < self.LEGAL_AGE
