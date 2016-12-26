class DBException(Exception):
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return self.msg


class MemNRDB:
    def __init__(self):
        self.tables = {}

    def __getitem__(self, table_name):
        try:
            return self.tables[table_name]
        except KeyError:
            raise DBException("Не найдена таблица с именем {}".format(table_name))

    def create_table(self, table_name: str):
        self.tables[table_name] = Table(table_name)


def _apply_class(row: dict, to_class: bool or 'Row'):
    if to_class is False:
        return row
    elif to_class is True:
        return Row(row)
    elif isinstance(to_class, Row):
        return to_class.__init__(row)


class Table:
    def __init__(self, name, convert=True):
        self.name = name
        self.data = list()  # type: list<dict>
        self.convert = convert
        self.index_count = 1
        self.meta_data = {}

    def insert(self, row):
        if isinstance(row, dict):
            # try to convert values to int
            if self.convert:
                for k, v in row.items():
                    try:
                        row[k] = float(v)
                        row[k] = int(v)
                    except Exception:
                        pass
            # check index
            if "id" in row:
                _id = row['id']
                if _id in self.meta_data:
                    raise DBException("Запись с данным id ({}) уже есть в таблице".format(_id))
            else:
                while self.index_count in self.meta_data:
                    self.index_count += 1
                _id = row["id"] = self.index_count
            # add row in table
            self.data.append(row)
            self.meta_data[_id] = row
        else:
            raise DBException("Запись должна быть типа dict, получено: {}".format(type(row)))
        return row

    def update(self, row: dict):
        if isinstance(row, dict):
            if 'id' in row:
                old_data = self.get(row['id'])
                old_data.update(row)
                return old_data
            else:
                raise DBException("Для обновления необходим id записи")
        else:
            raise DBException("Запись должна быть типа dict, получено: {}".format(type(row)))

    def rows(self, to_class: bool or 'Row'=False):
        for row in self.data:
            yield _apply_class(row, to_class)

    def get(self, _id: int, to_class: bool or 'Row'=False):
        try:
            return _apply_class(self.meta_data[_id], to_class)
        except KeyError:
            raise DBException("Элемента с таким id ({}) не найдено".format(_id))

    def query(self, q: "Query"):
        q.table = self
        return q


class Row:
    def __init__(self, raw: dict):
        self.data = raw

    def _get_raw_data(self):
        return self.data

    def __getitem__(self, item):
        return self.data[item]

    def __getattr__(self, item):
        return self.data[item]

    def __delete__(self, instance):
        return NotImplemented


class Query:
    def __init__(self, name, table: "Table" = None):
        self.name = name
        self.method_name = "_exist_field"
        self.test = None
        self.table = table

    def __call__(self, row: dict) -> dict or None:
        res = self._check(row)

        if res:
            return row
        else:
            return None

    def all(self, table: "Table" = None, to_class: bool or Row=False):
        if self.table and table:
            raise DBException("Таблица уже задана")
        table = table or self.table

        for row in table.rows():
            r = self(row)
            if r is not None:
                yield _apply_class(r, to_class)

    def limit(self, count: int, table: "Table" = None, to_class: bool or Row=False):
        for row in self.all(table=table, to_class=to_class):
            yield row
            count -= 1
            if 0 == count:
                return

    def _exist_field(self, row):
        return self.name in row

    def _check(self, row: dict) -> bool:
        if self._exist_field(row):
            if self.test is None:
                return True
            else:
                val = row[self.name]
                res = getattr(val, self.method_name)(self.test)
                if NotImplemented == res:
                    return False
                return True if res else False
        return False

    def __and__(self, other: "Query") -> "QueryLogic":
        if not isinstance(other, Query):
            raise DBException("Логические операции можно проводить только с запросами, а не с {}".format(type(other)))
        return QueryLogic("__and__", self, other)

    def __or__(self, other: "Query") -> "QueryLogic":
        if not isinstance(other, Query):
            raise DBException("Логические операции можно проводить только с запросами, а не с {}".format(type(other)))
        return QueryLogic("__or__", self, other)

    def _comparsion_filter_generator(self, method_name, other):
        self.method_name = method_name
        self.test = other
        return self

    def __eq__(self, other) -> "Query":
        return self._comparsion_filter_generator("__eq__", other)

    def __ne__(self, other) -> "Query":
        return self._comparsion_filter_generator("__ne__", other)

    def __lt__(self, other) -> "Query":
        return self._comparsion_filter_generator("__lt__", other)

    def __le__(self, other) -> "Query":
        return self._comparsion_filter_generator("__le__", other)

    def __ge__(self, other) -> "Query":
        return self._comparsion_filter_generator("__ge__", other)

    def __gt__(self, other) -> "Query":
        return self._comparsion_filter_generator("__gt__", other)

    def is_(self, other) -> "Query":
        # TODO: разобраться, почему не работает
        return self._comparsion_filter_generator("__is__", other)

    def is_not(self, other) -> "Query":
        # TODO: разобраться, почему не работает
        return self._comparsion_filter_generator("__is_not__", other)


class QueryLogic(Query):
    def __init__(self, method_name: str, left: Query, right: Query):
        self.method_name = method_name
        self.left = left
        self.right = right
        self.mt = getattr(True, self.method_name)
        self.mf = getattr(False, self.method_name)

    def _check(self, row: dict):
        return (self.mt if (self.left._check(row)) else self.mf)(self.right._check(row))
