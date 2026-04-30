from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class CustomerId:
    id: UUID
