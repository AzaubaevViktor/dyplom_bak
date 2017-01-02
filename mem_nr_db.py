import json
from typing import Dict, TypeVar
from typing import List


class DBException(Exception):
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return self.msg


class DBIndexError(DBException):
    def __init__(self, table: 'Table', operation: str, msg: str):
        self.table = table
        self.operation = operation
        self.msg = msg

    def __str__(self):
        return "DBIndexError в таблице `{}` во время операции `{}`: {}".format(
            self.table.name,
            self.operation,
            self.msg
        )


class DBTypeError(DBException):
    def __init__(self, table: 'Table', operation: str, obj_name: str, obj: object, need_type: type):
        self.table = table
        self.operation = operation
        self.obj_name = obj_name
        self.obj = obj
        self.need_type = need_type

    def __str__(self):
        return "DBTypeError в таблице `{}` во время операции `{}`: у переменной `{}` ожидается тип `{}`, получен `{}`".format(
            self.table.name,
            self.operation,
            self.obj_name,
            type(self.obj),
            self.need_type
        )


class MemNRDBEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, MemNRDB):
            return {'__MemNRDB__': True, '__tables__': o.tables}
        if isinstance(o, Table):
            return o.data
        return json.JSONEncoder.default(self, o)


def db_json_hook(dct):
    if '__MemNRDB__' in dct:
        tables = dct['__tables__']
        db = MemNRDB()
        for table_name, table_data in tables.items():
            table = db.init_table(table_name)
            for row in table_data:
                table.insert(row)
        return db
    return dct


class MemNRDB:
    """
    Нереляционная база данных, работающая в памяти.
    :Example:
    Создать БД
    >>> mdb = MemNRDB()
    >>> file_mdb = MemNRDB.load('db.json')

    Создать таблицу:
    >>> table = mdb.init_table('table_name')

    Получить таблицу по имени:
    >>> table = mdb['table_name']
    >>> table = mdb.init_table('table_name')

    Сохранить БД в файл:
    >>> file_mdb.serialize('db.json')

    """
    def __init__(self):
        self.tables = {}  # type: Dict[str, Table]

    def __getitem__(self, table_name: str) -> 'Table':
        """
        Возвращает таблицу через .
        :param table_name: название таблицы
        :return: таблица
        """
        try:
            return self.tables[table_name]
        except KeyError:
            raise DBException("Не найдена таблица с именем {}".format(table_name))

    def init_table(self, table_name: str) -> 'Table':
        """
        Вернуть таблицу по имени. Если её нет -- создать
        :param table_name:
        :return: таблица
        """
        if table_name in self.tables:
            t = self.tables[table_name]
        else:
            t = Table(table_name)
            self.tables[table_name] = t
        return t

    def __str__(self):
        return "<MemNRDB>, {} tables".format(len(self.tables))

    def serialize(self, file_name: str, pretty=False):
        """
        Загружает БД в файл
        :param file_name: Имя файла БД
        :param pretty: красивый вывод в файл
        :return:
        """
        kwargs = {
            "cls": MemNRDBEncoder,
            "ensure_ascii": False
        }
        if pretty:
            kwargs.update({
                "sort_keys": True,
                "indent": 4
            })
        json.dump(self, open(file_name, "wt"), **kwargs)

    @classmethod
    def load(cls, file_name: str) -> 'MemNRDB':
        """
        Загрузить бд из файла
        :param file_name: имя файла
        :return:
        """
        db = json.load(open(file_name, "rt"), object_hook=db_json_hook)
        if isinstance(db, MemNRDB):
            return db
        else:
            raise DBException("Не удалось загрузить базу из файла.")


def _apply_class(row: dict, to_class: bool or 'Row'):
    if to_class is False:
        return row
    elif to_class is True:
        return Row(row)
    else:
        return to_class(row)


class Table:
    """
    Таблица в БД
    :example:

    """
    def __init__(self, name: str, convert: bool =True):
        self.name = name
        self.data = list()  # type: List[dict]
        self.convert = convert
        self.index_count = 1
        self.meta_data = {}  # type: Dict[int, dict]

    def insert(self, row: dict) -> dict:
        """
        Вставить уникальную запись в таблицу (проверка на уникальный id)
        :param row: запись
        :return: запись из БД
        """
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
                    raise DBIndexError(self, 'insert', "Запись с данным id ({}) уже есть в таблице".format(_id))
            else:
                while self.index_count in self.meta_data:
                    self.index_count += 1
                _id = row["id"] = self.index_count
            # add row in table
            self.data.append(row)
            self.meta_data[_id] = row
        else:
            raise DBTypeError(self, "insert", 'row', row, dict)
        return row

    def update(self, row: dict) -> dict:
        """
        Обновить запись в БД (только если уже запись с таким id существует)
        :param row: новая запись
        :return: обновлённая запись из БД
        """
        if isinstance(row, dict):
            if 'id' in row:
                data = self.get(row['id'])
                data.update(row)
                return data
            else:
                raise DBIndexError(self, 'update', "не найден id записи")
        else:
            raise DBTypeError(self, "insert", 'row', row, dict)

    def ins_upd(self, row: dict) -> dict:
        """
        Создать или обновить запись в БД
        :param row: запись
        :return: запись из БД
        """
        try:
            return self.insert(row)
        except DBIndexError:
            pass

        return self.update(row)

    def rows(self, to_class: bool or 'Row'=False) -> dict or 'Row':
        """
        Возвращает записи, применяя или нет определённый класс
        :param to_class:
          False: не применять type:Row к записи;
          True: применять type:Row к записи;
          T <= Row: Применять T к записи
        :return:
        """
        for row in self.data:
            yield _apply_class(row, to_class)

    def get(self, _id: int, to_class: bool or 'Row'=False) -> dict or 'Row':
        """
        Вернуть запись по id
        :param _id: id записи
        :param to_class: обработка каждой записи
        :return:
        """
        try:
            return _apply_class(self.meta_data[_id], to_class)
        except KeyError:
            raise DBIndexError(self, 'get', "Элемента с таким id ({}) не найдено".format(_id))

    def query(self, q: "Query") -> 'Query':
        """ Вернуть запрос с прикреплённой таблицой """
        q.table = self
        return q

    def __str__(self):
        return "<MemNRDB.Table:{}>, {} rows".format(self.name, len(self.data))


class Row:
    """
    Класс обёртка для записи
    >>> row = Row({'val1': 1, 'val2': 2, 'list': [1, 2, 3], (1, 2): 'test'})

    >>> v = row['val1'] # 1
    >>> v = row.val1 # 1

    >>> row.non_exist # None

    >>> row['non_exist']
    Traceback (most recent call last):
        File "?", line ?, in ?
            row['non_exist']
    KeyError: 'non_exist'

    >>> v = row[(1, 2)] # 'test'

    >>> row['field'] = 'val'
    >>> row.field = 'val'
    """
    def __init__(self, raw: dict):
        object.__setattr__(self, "_data", raw)

    @property
    def _raw_data(self) -> dict:
        return self._data

    def __getitem__(self, item):
        return self._data[item]

    def __setitem__(self, key, value):
        self._data[key] = value

    def __getattr__(self, item):
        if '_data' == item:
            return self._raw_data
        else:
            return self._data.get(item, None)

    def __setattr__(self, key, value):
        self._data[key] = value

    def __delete__(self, instance):
        return NotImplemented


class Query:
    """ Класс-запрос к БД """
    @classmethod
    def ANY(cls) -> 'QueryAny':
        """ Возвращает экземпляр класса-запроса, которые пропускает любое поле """
        return QueryAny()

    def __init__(self, name, table: "Table" = None):
        self.path = name.split(".") if isinstance(name, str) else [name]
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
        return self._get_val_by_path(row) is not None

    def _get_val_by_path(self, row):
        _row = row
        for p in self.path:
            if p in _row:
                _row = _row[p]
            else:
                return None
        return _row

    def _check(self, row: dict) -> bool:
        if self._exist_field(row):
            if self.test is None:
                return True
            else:
                val = self._get_val_by_path(row)
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


class QueryAny(Query):
    def __init__(self):
        super().__init__("__any_not_used__")

    def _check(self, row: dict):
        return True


class QueryLogic(Query):
    def __init__(self, method_name: str, left: Query, right: Query):
        self.method_name = method_name
        self.left = left
        self.right = right
        self.mt = getattr(True, self.method_name)
        self.mf = getattr(False, self.method_name)

    def _check(self, row: dict):
        return (self.mt if (self.left._check(row)) else self.mf)(self.right._check(row))
