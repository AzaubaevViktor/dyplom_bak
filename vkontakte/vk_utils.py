from time import sleep

from typing import List, Iterable

from vk import API as VkAPI
from vk.api import Request as VkRequest
from vk.exceptions import VkAPIError

from .models import VkUser, VkPost
from .utils import extend_nested_list


class API(VkAPI):
    """
    Модуль-обвязка для vk.API
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

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
            user = VkUser(row=user_data)
            if user.is_deactivated:
                continue
            user.save()
            yield user

    def get_wall_posts(self, users: List['User'], count=100, from_time=-1) -> Iterable['Post']:
        answer = self.execute.wallWatch(
            id_list=[user.id for user in users],
            count=count
        )

        for row in extend_nested_list(answer):
            post = VkPost(row)
            post.find_user()
            post.save()
            return post


class Request(VkRequest):
    """ Модуль-обвязка для vk.Request, обрабатывающая ошибки """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

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
                else:
                    raise e
