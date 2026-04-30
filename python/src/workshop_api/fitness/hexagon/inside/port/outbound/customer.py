from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class Customer:
    date_of_birth: date
    email_address: str
