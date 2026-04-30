from uuid import UUID

from sqlalchemy.orm import Session

from workshop_api.fitness.infrastructure.customer_entity import CustomerOrmModel


class CustomerRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def find_all(self) -> list[CustomerOrmModel]:
        return self.session.query(CustomerOrmModel).all()

    def find_by_id(self, customer_id: UUID) -> CustomerOrmModel | None:
        return self.session.get(CustomerOrmModel, str(customer_id))

    def save(self, customer: CustomerOrmModel) -> CustomerOrmModel:
        self.session.add(customer)
        self.session.commit()
        self.session.refresh(customer)
        return customer

    def delete(self, customer: CustomerOrmModel) -> None:
        self.session.delete(customer)
        self.session.commit()
