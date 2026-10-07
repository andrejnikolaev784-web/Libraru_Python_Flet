from typing import Generic, Iterator, List, Optional, TypeVar

K = TypeVar("K")
V = TypeVar("V")

class EntityMap(Generic[K, V]):

    def __init__(self) -> None:
        self._keys: List[K] = []
        self._values: List[V] = []

    def put(self, key: K, value: V) -> V:
        i = self._index(key)
        if i is None:
            self._keys.append(key)
            self._values.append(value)
        else:
            self._values[i] = value
        return value

    def get(self, key: K) -> Optional[V]:
        i = self._index(key)
        return None if i is None else self._values[i]

    def values(self) -> List[V]:
        return list(self._values)

    def __len__(self) -> int:
        return len(self._keys)

    def __iter__(self) -> Iterator[V]:
        return iter(self._values)

    def _index(self, key: K) -> Optional[int]:
        for i, k in enumerate(self._keys):
            if k == key:
                return i
        return None