import random
from time import sleep

import vk
from vk import API as VkAPI
from vk.api import Request as VkRequest
from vk.exceptions import VkAPIError

from mem_nr_db import Row, Table


class API(VkAPI):
    def __getattr__(self, method_name):
        return Request(self, method_name)


class Request(VkRequest):
    def __getattr__(self, method_name):
        return Request(self._api, self._method_name + '.' + method_name)

    def __call__(self, *args, **kwargs):
        while True:
            try:
                return super().__call__(*args, **kwargs)
            except VkAPIError as e:
                if 6 == e.code:
                    print(e.message)
                    sleep(1)


def address_to_dict(addr: str) -> dict:
    # noinspection PyTypeChecker
    return dict(
        x.split("=") for x in
        addr.split("/")[-1]
            .split("#")[-1]
            .split("&")
    )


class VkInit:
    def __init__(self, app_id: str, token_file: str):
        self._app_id = app_id
        self._token_file = token_file
        self._token = None
        self._session = None
        self._api = None

    @property
    def token(self):
        if not self._token:
            try:
                self._token = open(self._token_file, "rt").read() or self._authorize()
            except FileNotFoundError:
                self._token = self._authorize()

            open(self._token_file, "wt").write(self._token)

        return self._token

    @property
    def api(self):
        if not self._api:
            self._session = vk.Session(access_token=self.token)
            self._api = API(self._session, v='5.60', lang='ru')
        return self._api

    def disconnect(self):
        self._api = None
        self._session = None
        self._token = None

    def _authorize(self):
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
    def __init__(self, _id: int or str):
        self.members_count = -1
        self._id = _id

    def get_members(self, api: API):
        count = 0
        while self.members_count == -1 or count < self.members_count:
            data = api.groups.getMembers(group_id=self._id, offset=count, count=1000)
            print(count)
            ids = data['items']
            self.members_count = data['count']
            count += len(ids)
            yield ids


def get_wall_posts(api: API, ids: list, count: int, from_time=-1):
    # TODO: переделать ids на users
    answer = api.execute.wallWatch(
        id_list=ids,
        count=count
    )
    for posts in answer:
        if posts:
            for item in posts:
                dt = item['date']
                text = item['text']
                likes = item['likes']['count']
                reposts = item['reposts']['count']

                if -1 != from_time and dt > from_time:
                    yield dt, text, likes, reposts


class User:
    def __init__(self, row: dict):
        self.row = row
        if 'cost' not in self.row:
            self.row['cost'] = {}

    @property
    def id(self):
        return self.row['id']

    def get_friends(self):
        return NotImplemented

    def load_to(self, table: Table):
        table.ins_upd(self.row)

    @classmethod
    def load_from(cls, table: Table, _id: int):
        return User(table.get(_id))

    @property
    def cost(self):
        return self.row['cost']

    @cost.setter
    def cost(self, value):
        self.row['cost'] = value

    def __str__(self):
        return "<User#{}>: {} {}".format(
            self.id,
            self.row.get('first_name', "---"),
            self.row.get('second_name', "---")
        )


def get_users(api, ids: int or list):
    users_data = api.users.get(
        user_ids=ids,
        fields=['bdate', 'city', 'connections', 'education', 'exports', 'personal', 'relations', 'sex', 'universities']
    )
    for user_data in users_data:
        yield User(user_data)
