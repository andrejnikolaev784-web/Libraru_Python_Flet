from abc import ABC, abstractmethod
from datetime import date, timedelta
from typing import Optional
from uuid import uuid4

class Entity(ABC):
    def __init__(self) -> None:
        self._id: str = str(uuid4())

    @property
    def id(self) -> str:
        return self._id

    @id.setter
    def id(self, value: str) -> None:
        if not value:
            raise ValueError("id пустой")
        self._id = value

    @abstractmethod
    def summary(self) -> str:
        ...

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Entity):
            return NotImplemented
        return self._id == other._id

    def __lt__(self, other: object) -> bool:
        if not isinstance(other, Entity):
            return NotImplemented
        return self.summary() < other.summary()

    def __le__(self, other: object) -> bool:
        return self == other or self < other

    def __gt__(self, other: object) -> bool:
        if not isinstance(other, Entity):
            return NotImplemented
        return other < self

    def __ge__(self, other: object) -> bool:
        return self == other or self > other

    def __hash__(self) -> int:
        return hash(self._id)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(id={self._id!r})"

    def __str__(self) -> str:
        return self.summary()

class CatalogItem(Entity):
    def __init__(self, title: str) -> None:
        super().__init__()
        self._title = title
        self._available = True

    @property
    def title(self) -> str:
        return self._title

    @title.setter
    def title(self, value: str) -> None:
        value = value.strip()
        if not value:
            raise ValueError("Название пустое")
        self._title = value

    @property
    def available(self) -> bool:
        return self._available

    @available.setter
    def available(self, value: bool) -> None:
        self._available = bool(value)

    def mark_issued(self) -> None:
        if not self._available:
            raise ValueError(f"«{self._title}» уже выдано")
        self._available = False

    def mark_returned(self) -> None:
        self._available = True

class Book(CatalogItem):
    def __init__(self, title: str, author: str, year: int) -> None:
        super().__init__(title)
        self._author = author
        self._year = year

    @property
    def author(self) -> str:
        return self._author

    @author.setter
    def author(self, value: str) -> None:
        value = value.strip()
        if not value:
            raise ValueError("Автор пустой")
        self._author = value

    @property
    def year(self) -> int:
        return self._year

    @year.setter
    def year(self, value: int) -> None:
        value = int(value)
        if value < 1:
            raise ValueError("Некорректный год")
        self._year = value

    def summary(self) -> str:
        st = "в зале" if self.available else "на руках"
        return f"Книга: {self._author} — {self.title} ({self._year}) · {st}"

class Magazine(CatalogItem):
    def __init__(self, title: str, issue: int) -> None:
        super().__init__(title)
        self._issue = issue

    @property
    def issue(self) -> int:
        return self._issue

    @issue.setter
    def issue(self, value: int) -> None:
        value = int(value)
        if value < 1:
            raise ValueError("Некорректный номер")
        self._issue = value

    def summary(self) -> str:
        st = "в зале" if self.available else "на руках"
        return f"Журнал: «{self.title}» №{self._issue} · {st}"

class Reader(Entity):
    def __init__(self, name: str, ticket: str) -> None:
        super().__init__()
        self._name = name
        self._ticket = ticket

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        value = value.strip()
        if not value:
            raise ValueError("ФИО пустое")
        self._name = value

    @property
    def ticket(self) -> str:
        return self._ticket

    @ticket.setter
    def ticket(self, value: str) -> None:
        value = value.strip()
        if not value:
            raise ValueError("Билет пустой")
        self._ticket = value

    def summary(self) -> str:
        return f"{self._name} (билет {self._ticket})"

class Loan(Entity):
    def __init__(self, item: CatalogItem, reader: Reader, due: date) -> None:
        super().__init__()
        self._item = item
        self._reader = reader
        self._due = due
        self._returned = False

    @property
    def item(self) -> CatalogItem:
        return self._item

    @item.setter
    def item(self, value: CatalogItem) -> None:
        self._item = value

    @property
    def reader(self) -> Reader:
        return self._reader

    @reader.setter
    def reader(self, value: Reader) -> None:
        self._reader = value

    @property
    def due(self) -> date:
        return self._due

    @due.setter
    def due(self, value: date) -> None:
        self._due = value

    @property
    def returned(self) -> bool:
        return self._returned

    @returned.setter
    def returned(self, value: bool) -> None:
        self._returned = bool(value)

    def is_overdue(self, today: Optional[date] = None) -> bool:
        today = today or date.today()
        return (not self._returned) and today > self._due

    def summary(self) -> str:
        if self._returned:
            flag = "возвращено"
        elif self.is_overdue():
            flag = "просрочено"
        else:
            flag = "активно"
        return f"{self._item.title} → {self._reader.name} до {self._due} ({flag})"