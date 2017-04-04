from pprint import pprint
from time import sleep

from typing import List, Iterable

from vk import API as VkAPI
from vk.api import Request as VkRequest
from vk.exceptions import VkAPIError

from .models import VkUser, VkPost, VkGroup
from .utils import extend_nested_list


class API(VkAPI):
    """
    Модуль-обвязка для vk.API
    """
    user_fields = ['bdate', 'city', 'connections', 'education', 'exports', 'personal', 'relations', 'sex',
                   'universities']

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
        answer = self.users.get(
            user_ids=ids,
            fields=self.user_fields
        )
        users = []
        for row in answer:
            user = VkUser(row=row)
            if user.is_deactivated:
                continue
            user.save()
            users.append(user)
        return users

    def get_wall_posts(self, users: List['User'], count=100, from_time=-1) -> Iterable['Post']:
        answer = self.execute.wallWatch(
            id_list=[user.id for user in users],
            count=count,
            func_v=4
        )

        posts = []

        for row in extend_nested_list(answer):
            post = VkPost(row=row)
            post.find_user()
            post.save()
            posts.append(post)

        return posts

    def get_groups(self, group_ids: List[int or str]):
        answer = self.groups.getById(
            group_ids=group_ids,
        )
        groups = []
        for row in answer:
            group = VkGroup(row=row)
            group.save()
            groups.append(group)
        return groups

    def get_group_users(self, group: VkGroup):
        offset = 0
        count = 1
        while offset < count:
            answer = self.groups.getMembers(
                group_id=group.id,
                offset=offset,
                count=1000,
                sort='id_desc'
            )
            count = answer['count']
            offset += 1000
            ids = answer['items']
            users = self.get_users(ids)
            group.users.add(*users)
            yield from users


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
            except Exception as e:
                sleep(5)
                print("Sleep, error {}".format(e))
            # except VkAPIError as e:
            #     if 6 == e.code:
            #         self.log.info("Error: \n  %s", e.message)
            #         sleep(1)
            #     else:
            #         raise e
