import json
from typing import Dict, TypeVar, Iterable
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

    >>> t = Table("table")

    >>> row = t.insert({'a': 1, 'b': 2})

    Каждой строке при создании присваивается новый id:
    >>> row['id']
    1

    id можно указывать вручную:
    >>> row5 = t.insert({'id': 5, 'c': 3})
    >>> row5['id']
    5

    Если нужно обновить запись:
    >>> row5 = t.update({'id': 5, 'd': 4})
    >>> row5['d']
    4
    >>> row5['c']
    3

    Если нужно удалить поле из записи:
    >>> row5 = t.update({'id': 5, 'c': None})
    >>> row5['c']
    Traceback (most recent call last):
      File "?", line ?, in ?
        row5['c']
    KeyError: 'c'

    Обновлять ещё не созданные записи нельзя:
    >>> row6 = t.update({'id': 6, 'val': 'val'})
    Traceback (most recent call last):
      File "?", line ?, in ?
        raise DBIndexError(...)
    mem_nr_db.DBIndexError: DBIndexError в таблице `table` во время операции `get`: Элемента с таким id (6) не найдено

    Если неизвестно, есть ли запись с id в табице, то:
    >>> row6 = t.ins_upd({'id': 6, 'val': 'val'})
    >>> row6['id']
    6
    """
    def __init__(self, name: str, convert: bool = True):
        self.name = name
        self.data = list()  # type: List[dict]
        self.convert = convert  # Конвертировать ли переменные в числа автоматически
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
                if not isinstance(_id, int):
                    raise DBIndexError(self, 'insert', "поле id должен быть числом, а не `{}` ({})".format(_id, type(_id)))
                if _id in self.meta_data:
                    raise DBIndexError(self, 'insert', "Запись с данным id ({}) уже есть в таблице".format(_id))
            else:
                # create index
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
                _to_del = []
                for k, v in data.items():
                    if v is None:
                        _to_del.append(k)
                for k in _to_del:
                    del data[k]
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

    def rows(self, to_class: bool or 'Row'=False) -> Iterable[dict or 'Row']:
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

    >>> row['val1']
    1

    >>> row.val1
    1

    >>> row.non_exist  # None

    >>> row['non_exist']
    Traceback (most recent call last):
        File "?", line ?, in ?
            row['non_exist']
    KeyError: 'non_exist'

    >>> row[(1, 2)]
    'test'

    >>> row['field'] = 'val'
    >>> row.field = 'val'
    >>> row.field
    'val'
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
    """ Класс-запрос к БД

    Создаст запрос, который вернёт все поля, в которых:
         .--* поле field существует и меньше 123
    .---или
    |    `--* поле field2 существует и не равно 'string'
    и
    `---* поле field3 сществует
    >>> q = ((Query("field") < 123) | (Query("field2") != "string")) & (Query("field3"))

    Можно указать таблицу руками:
    >>> t = Table('table')
    >>> q.table = t

    Либо передать запрос таблице:
    >>> q_t = t.query(q)

    # TODO: Написать нормальный вывод, с list и что происходит внутри

    После этого можно попросить у таблицы либо все записи:
    >>> q.all() # doctest: +ELLIPSIS
    <generator object Query.all at 0x...>

    Либо определённое количество:
    >>> q.limit(100) # doctest: +ELLIPSIS
    <generator object Query.limit at 0x...>

    Всё составление запроса можно уместить в одну строчку:
    >>> t.query(Query("field") < 123).all() # doctest: +ELLIPSIS
    <generator object Query.all at 0x...>

    Также можно преобразовывать результаты в нужный класс:
    >>> class SomeClassRow(Row):
    ...     pass
    >>> q.all(to_class=SomeClassRow) # doctest: +ELLIPSIS
    <generator object Query.all at 0x...>

    Либо во встроенный:
    >>> q.limit(100, to_class=True) # doctest: +ELLIPSIS
    <generator object Query.limit at 0x...>

    """
    @classmethod
    def ANY(cls) -> 'QueryAny':
        """ Возвращает экземпляр класса-запроса, которые пропускает любое поле """
        return QueryAny()

    def __init__(self, name: str or object, table: "Table" = None):
        self.path = name.split(".") if isinstance(name, str) else [name]  # адрес поля
        self.test_method_name = "_exist_field"  # метод: который будет вызываться у значения для проверки
        self.test_value = None  # значение проверки
        self.table = table  # ассоциированная таблица, из которой берутся записи

    def __call__(self, row: dict) -> dict or None:
        """
        Проверяет запись в соответствии с фильтром
        :param row: запись
        :return: Строка или ничего, в зависимости от того, прошёл ли тест
        """
        res = self._check(row)

        if res:
            return row
        else:
            return None

    def all(self, table: "Table" = None, to_class: bool or Row=False) -> Iterable[Row]:
        """
        Возвращает все прошедшие фильтр записи
        :param table: таблица, если не задана
        :param to_class: преобразование в класс
        :return: записи
        """
        if self.table and table:
            raise DBException("Таблица уже задана")
        table = table or self.table

        for row in table.rows():
            r = self(row)
            if r is not None:
                yield _apply_class(r, to_class)

    def limit(self, count: int, table: "Table" = None, to_class: bool or Row=False) -> Iterable[Row]:
        """
        Возвращает count записей, прошедших фильтр
        :param count: кол-во записей, которые нужно вернуть
        :param table: таблица, если не задана
        :param to_class: преобразование в класс
        :return: записи
        """
        for row in self.all(table=table, to_class=to_class):
            yield row
            count -= 1
            if 0 == count:
                return

    def _exist_field(self, row: dict or Row) -> bool:
        """ Проверяет, существует ли поле """
        return self._get_val_by_path(row) is not None

    def _get_val_by_path(self, row: dict or Row) -> dict or Row or None:
        """ Возвращает значение нужного поля по адресу в self.path, если оно есть """
        _row = row
        for p in self.path:
            if p in _row:
                _row = _row[p]
            else:
                return None
        return _row

    def _check(self, row: dict or Row) -> bool:
        """
        Проверяет, проходит ли запись через фильтр
        :param row: запись
        :return:
        """
        if self._exist_field(row):
            if self.test_value is None:
                return True
            else:
                # Получаем значение
                val = self._get_val_by_path(row)
                # Проверяем условие
                res = getattr(val, self.test_method_name)(self.test_value)
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

    def _comparison_filter_generator(self, test_method_name: str, test_value: object):
        """ Задаёт, какую операцию с чем выполнить """
        self.test_method_name = test_method_name
        self.test_value = test_value
        return self

    def __eq__(self, other) -> "Query":
        return self._comparison_filter_generator("__eq__", other)

    def __ne__(self, other) -> "Query":
        return self._comparison_filter_generator("__ne__", other)

    def __lt__(self, other) -> "Query":
        return self._comparison_filter_generator("__lt__", other)

    def __le__(self, other) -> "Query":
        return self._comparison_filter_generator("__le__", other)

    def __ge__(self, other) -> "Query":
        return self._comparison_filter_generator("__ge__", other)

    def __gt__(self, other) -> "Query":
        return self._comparison_filter_generator("__gt__", other)

    def is_(self, other) -> "Query":
        # TODO: разобраться, почему не работает
        return self._comparison_filter_generator("__is__", other)

    def is_not(self, other) -> "Query":
        # TODO: разобраться, почему не работает
        return self._comparison_filter_generator("__is_not__", other)


class QueryAny(Query):
    """ Класс-запрос для запроса 'любой' """
    def __init__(self):
        super().__init__("__any_not_used__")

    def _check(self, row: dict) -> bool:
        return True


class QueryLogic(Query):
    """ Класс запрос для работы с & и | (логическое `и` и `или` в данном контексте)"""
    def __init__(self, method_name: str, left: Query, right: Query):
        self.method_name = method_name
        self.left = left
        self.right = right
        self.mt = getattr(True, self.method_name)
        self.mf = getattr(False, self.method_name)

    def _check(self, row: dict) -> bool:
        return (self.mt if (self.left._check(row)) else self.mf)(self.right._check(row))
