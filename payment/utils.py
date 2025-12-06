from collections.abc import MutableMapping
from typing import TypeVar, Iterator

_T = TypeVar('_T')


class KeyPrefix(MutableMapping[str, _T]):
    def __init__(self, mapping: MutableMapping[str, _T], prefix: str):
        self._prefix = prefix
        self._mapping = mapping

    def __setitem__(self, key: str, value: _T, /):
        self._mapping[self._prefix + key] = value

    def __delitem__(self, key: str, /):
        del self._mapping[self._prefix + key]

    def __getitem__(self, key: str, /) -> _T:
        return self._mapping[self._prefix + key]

    def __len__(self) -> int:
        c = 0
        for k in self._mapping:
            if k.startswith(self._prefix):
                c += 1
        return c

    def __iter__(self) -> Iterator[str]:
        return iter(k.removeprefix(self._prefix) for k in self._mapping if k.startswith(self._prefix))

    def __repr__(self):
        return "{}({})".format(self.__class__.__name__, self)

    def __str__(self):
        return "{" + ", ".join("{!r}:{!r}".format(k, v) for k, v in self.items()) + "}"


class DefaultKeyPrefix(KeyPrefix[str, _T]):
    def __init__(self, mapping: MutableMapping[str, _T], prefix: str, default=None):
        super().__init__(mapping, prefix)
        if not callable(default):
            default = lambda: default
        self._default = default

    def __getitem__(self, key: str, /) -> _T:
        key = self._prefix + key
        if key not in self._mapping:
            result = self._mapping[key] = self._default()
            return result
        return self._mapping[key]
