from typing import Generic, List, Optional, TypeVar

from mapping import EntityMap
from models import CatalogItem, Entity, Loan, Reader

T = TypeVar("T", bound=Entity)

class InMemoryRepository(Generic[T]):
    def __init__(self) -> None:
        self._store: EntityMap[str, T] = EntityMap()

    def add(self, entity: T) -> T:
        return self._store.put(entity.id, entity)

    def get(self, entity_id: str) -> Optional[T]:
        return self._store.get(entity_id)

    def all(self) -> List[T]:
        return self._store.values()

class LoanStore:
    def __init__(self) -> None:
        self._store: EntityMap[str, Loan] = EntityMap()

    def add(self, loan: Loan) -> Loan:
        return self._store.put(loan.id, loan)

    def get(self, loan_id: str) -> Optional[Loan]:
        return self._store.get(loan_id)

    def all(self) -> List[Loan]:
        return self._store.values()