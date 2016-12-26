import random

import vk


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
            self._api = vk.API(self._session)
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


