import logging
import random

import vk
from typing import List, Iterable

from prog.mem_nr_db import Table

logging.getLogger("VkUtils").setLevel(logging.WARNING)






class VkInit:
    """ Класс для подключения к API VK """
    def __init__(self, app_id: str, token_file_name: str):
        """
        :param app_id: ID приложения
        :param token_file_name: расположение файла с токеном пользователя
        """
        self._app_id = app_id
        self._token_file_name = token_file_name
        self._token = None
        self._session = None
        self._api = None

    @property
    def token(self) -> str:
        """
        Возвращает токен, если есть; если нет -- получает его
        :return: токен пользователя
        """
        if not self._token:
            try:
                self._token = open(self._token_file_name, "rt").read() or self._authorize()
            except FileNotFoundError:
                self._token = self._authorize()

            open(self._token_file_name, "wt").write(self._token)

        return self._token

    @property
    def api(self) -> API:
        """
        Возвращает экземпляр API; если нет -- создаёт его
        :return: Экземпляр API VK
        """
        if not self._api:
            self._session = vk.Session(access_token=self.token)
            self._api = API(self._session, v='5.60', lang='ru')
        return self._api

    def disconnect(self):
        """ Отключается от VK """
        self._api = None
        self._session = None
        self._token = None

    def _authorize(self) -> str:
        """
        Авторизует пользователя в приложении и вовращает токен
        :return: токен пользователя
        """
        link_fmt = "https://oauth.vk.com/authorize?client_id={app_id}&display=page&redirect_uri=https://oauth.vk.com/blank.html&scope={scope}&response_type=token&v=5.60&state={state}"
        state = random.random()
        scope = ["friends", "wall", "offline", "groups"]
        link = link_fmt.format(
            app_id=self._app_id,
            scope=",".join(scope),
            state=state
        )
        data = dict()
        while not data:
            print("Для авторизации перейди по следующей ссылке и скопируй данные из адресной строки: {}".format(link))
            try:
                data = address_to_dict(input("> "))
            except Exception:
                print("Неверный адрес. Попробуй ещё раз!")
        return data['access_token']


class Post:
    def __init__(self, row: dict):
        self.row = row
        self.date = self.row['date']
        self.owner_id = self.row['owner_id']
        self.id = self.row['id']
        self.text = self.row['text']
        self.reposts = self.row['reposts']['count']
        self.likes = self.row['likes']['count']

    def _find_source(self):
        copy_history = self.row.get('copy_history', {})
        self.source = {
            'owner_id': copy_history.get('owner_id'),
            'id': copy_history.get('id')
        }


class Group:
    """ Класс-обвязка для группы вконтакте """
    def __init__(self, _id: int or str):
        self.members_count = -1
        self._id = _id
        self.log = logging.getLogger("VkUtils.VkGroup")

    def get_members(self, api: API) -> Iterable[List[int]]:
        """
        Возвращает генератор со списками id пользователей
        :param api: экземпляр VK API
        :return: генератор со списком пользователей
        """
        count = 0
        while self.members_count == -1 or count < self.members_count:
            data = api.groups.getMembers(group_id=self._id, offset=count, count=1000)
            self.log.debug("Получено пользователей: {}".format(count))
            ids = data['items']
            self.members_count = data['count']
            count += len(ids)
            yield ids


class User:
    """ Класс-обёртка над пользователем VK """
    def __init__(self, row: dict):
        self.row = row
        self.id = self.row['id']
        self.sex = self.row['sex']
        self.first_name = self.row['first_name']
        self.last_name = self.row['last_name']
        self._bdate = self.row.get('bdate')
        self.university = self.row.get('university', -1)
        self.graduation = self.row.get('graduation', -1)

        if 'cost' not in self.row:
            self.row['cost'] = {}

    @property
    def in_NSU(self):
        return 671 == self.university

    def get_friends(self):
        return NotImplemented

    def load_to(self, table: Table):
        """
        Загружает пользователя в таблицу
        :param table: Таблица из БД
        """
        table.ins_upd(self.row)

    @classmethod
    def load_from(cls, table: Table, _id: int) -> "User":
        """
        Загружает пользователя из таблицы
        :param table: Таблица из БД
        :param _id: ID пользователя в VK
        :return: Пользователь
        """
        return User(table.get(_id))

    @property
    def cost(self) -> float:
        """ Возвращает список с значениями того, что человек в НГУ """
        return self.row['cost']

    def __str__(self):
        return "<User#{}>: {} {}".format(
            self.id,
            self.row.get('first_name', "???"),
            self.row.get('last_name', "???")
        )


