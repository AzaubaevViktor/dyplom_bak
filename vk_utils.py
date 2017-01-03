import random
from time import sleep
from typing import Iterator, List, Generator, Generic, Iterable, Tuple

import logging
import vk
from vk import API as VkAPI
from vk.api import Request as VkRequest
from vk.exceptions import VkAPIError

from mem_nr_db import Row, Table


class API(VkAPI):
    """
    Модуль-обвязка для vk.API
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.log = logging.getLogger("VkAPI-Bind")

    def __getattr__(self, method_name: str):
        return Request(self, method_name)

    def get_users(self, ids: int or List[int]):
        """
        Выполняет запрос к API VK и получает пользователей VK
        :param self:
        :param ids:
        :return:
        """
        users_data = self.users.get(
            user_ids=ids,
            fields=['bdate', 'city', 'connections', 'education', 'exports', 'personal', 'relations', 'sex',
                    'universities']
        )
        for user_data in users_data:
            yield User(user_data)

    def get_wall_posts(self, users: List["User"], count: int, from_time=-1) -> Iterable[Tuple[str, str, str, int, int]]:
        """
        Возвращает посты
        :param users: Список пользователей
        :param count: сколько постов дергать
        :param from_time: и с какого времени
        :return: Посты
        """
        # TODO: переделать в посты
        answer = self.execute.wallWatch(
            id_list=[user.id for user in users],
            count=count
        )
        for user, posts in zip(users, answer):  # type: (User, List[dict] | List[None])
            if posts:
                for item in posts:
                    dt = item['date']
                    text = item['text']
                    likes = item['likes']['count']
                    reposts = item['reposts']['count']

                    if -1 != from_time and text and dt > from_time:
                        yield user, dt, text, likes, reposts


class Request(VkRequest):
    """ Модуль-обвязка для vk.Request, обрабатывающая ошики """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.log = logging.getLogger("VkRequest-Bind")

    def __getattr__(self, method_name):
        return Request(self._api, self._method_name + '.' + method_name)

    def __call__(self, *args, **kwargs):
        while True:
            try:
                return super().__call__(*args, **kwargs)
            except VkAPIError as e:
                if 6 == e.code:

                    self.log.info("Error: \n  %s", e.message)
                    sleep(1)


def address_to_dict(addr: str) -> dict:
    """
    Достаёт из адреса GET параметры
    :param addr: адрес
    :return: список GET-параметров
    """
    # noinspection PyTypeChecker
    return dict(
        x.split("=") for x in
        addr.split("/")[-1]
            .split("#")[-1]
            .split("&")
    )


class VkInit:
    """ Класс для подключения к API VK """
    def __init__(self, app_id: str, token_file_name: str):
        """
        :param app_id: ID приложения
        :param token_file_name: расположение файла с токеном полбзователя
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


class Group:
    """ Класс-обвязка для группы вконтакте """
    def __init__(self, _id: int or str):
        self.members_count = -1
        self._id = _id
        self.log = logging.getLogger("VkGroup")

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
        if 'cost' not in self.row:
            self.row['cost'] = {}

    @property
    def id(self) -> int:
        return self.row['id']

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
            self.row.get('first_name', "---"),
            self.row.get('last_name', "---")
        )


