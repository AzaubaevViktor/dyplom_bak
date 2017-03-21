from typing import Dict, Callable
from typing import List
import re

from copy import copy


class DB:
    def __init__(self):
        self.tables = {}  # type: Dict[str, Table]

    def create_table(self, table_name):
        new_table = Table()
        self.tables[table_name] = new_table
        return new_table


class Table:
    def __init__(self):
        self.rows = []  # type: List[dict]
        self.indexes = []  # type: List[Index]

    def create_index(self, index: 'Index'):
        self.indexes.append(index)

    def append(self, row: dict):
        self.rows.append(row)
        for index in self.indexes:
            index(row)

    def __iter__(self):
        return iter(self.rows)


class Filter:
    def __init__(self):
        self.lookups = []
        self.method = ""
        self.value = None

    def __copy__(self) -> 'Filter':
        f = Filter()
        f.lookups = self.lookups[:]
        f.method = self.method
        f.value = copy(f.value)
        return f

    def __getattr__(self, item) -> 'Filter':
        f = copy(self)
        f.lookups.append(
            lambda res, x: res.append(x[item])
        )
        return f

    def __getitem__(self, item) -> 'Filter':
        f = copy(self)
        f.lookups.append(
            lambda res, x:
                res.extend(x[item])
                if isinstance(item, slice)
                else res.append(x[item])
        )
        return f

    def __method_base__(self, method, other) -> 'Filter':
        f = copy(self)
        f.method = method
        f.value = other
        return f

    def __eq__(self, other) -> 'Filter':
        return self.__method_base__("__eq__", other)

    def _check_row(self, row):
        result = [row]
        # check values

        for lookup in self.lookups:
            new_result = []

            try:
                for item in result:
                    lookup(new_result, item)
            except (ValueError,
                    KeyError,
                    TypeError,
                    IndexError,
                    AttributeError):
                return False

            result = new_result

        for item in result:
            try:
                v = getattr(item, self.method)(self.value)
                if True is not v:
                    return False
            except AttributeError:
                return False

        return True

    def __call__(self, rows):
        for row in iter(rows):
            if self._check_row(row):
                yield row


class Index:
    def __init__(self, field: str,
                 unique: bool = False,
                 not_none: bool = False,
                 auto_increment: bool = False
                 ):
        self.field = field
        self.unique = unique
        self.not_none = not_none
        self.auto_increment = auto_increment
        self.data = {None: []}  # type: Dict[object, List[dict]]

    def __call__(self, row: dict):
        if self.field in row:
            value = row[self.field]
            if value not in self.data:
                self.data[value] = []

            if value in self.data:
                if len(self.data[value]) and self.unique:
                    raise ValueError(
                        "Duplicate value: row `{}`, field `{}`, value `{}`".format(
                            row,
                            self.field,
                            value
                        )
                    )
                self.data[value].append(row)
        else:
            if self.not_none:
                raise ValueError(
                    "Duplicate value: row `{}`, field `{}`".format(
                        row,
                        self.field
                    )
                )
            self.data[None].append(row)
