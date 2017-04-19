from datetime import date, datetime

from django.contrib.postgres.fields import JSONField
from django.db import models
import random

# Create your models here.
from django.utils.html import format_html

from .utils import parse_date


class VkConnector(models.Model):
    app_id = models.CharField(max_length=50)
    _token = models.CharField(max_length=200)

    @classmethod
    def default(cls) -> 'VkConnector':
        return cls.objects.get(id=1)

    @property
    def token(self) -> str:
        """
        Возвращает токен, если есть; если нет -- получает его
        :return: токен пользователя
        """
        if not self._token:
            self._token = self._authorize()
        return self._token

    @property
    def api(self) -> 'API':
        if not hasattr(self, '_api'):
            import vk
            from .vk_utils import API
            self._session = vk.Session(access_token=self.token)
            self._api = API(self._session, v='5.63', lang='ru')
        return self._api

    @staticmethod
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

    def _authorize(self) -> str:
        """
        Авторизует пользователя в приложении и вовращает токен
        :return: токен пользователя
        """
        link_fmt = "https://oauth.vk.com/authorize?client_id={app_id}&display=page&redirect_uri=https://oauth.vk.com/blank.html&scope={scope}&response_type=token&v=5.60&state={state}"
        state = random.random()
        scope = ["friends", "wall", "offline", "groups"]
        link = link_fmt.format(
            app_id=self.app_id,
            scope=",".join(scope),
            state=state
        )
        data = dict()
        while not data:
            print("Для авторизации перейди по следующей ссылке и скопируй данные из адресной строки: {}".format(link))
            try:
                data = self.address_to_dict(input("> "))
            except Exception:
                print("Неверный адрес. Попробуй ещё раз!")
        return data['access_token']


class VkUser(models.Model):
    SEX = (
        (0, 'Unknown'),
        (1, 'Woman'),
        (2, 'Man')
    )
    row = JSONField()
    sex = models.SmallIntegerField(choices=SEX)
    first_name = models.CharField(max_length=100, default="")
    last_name = models.CharField(max_length=100, default="")

    year = models.IntegerField(default=None, null=True)
    month = models.IntegerField(default=None, null=True)
    day = models.IntegerField(default=None, null=True)

    university = models.IntegerField(default=0)  # университет
    graduation = models.IntegerField(default=0)  # год выпуска
    faculty = models.IntegerField(default=0)  # факультет

    def save(self, *args, **kwargs):
        self._fill()
        return super().save(*args, **kwargs)

    def _fill(self):
        self.id = self.row['id']
        self.sex = int(self.row['sex'])
        self.first_name = self.row['first_name']
        self.last_name = self.row['last_name']
        self._fill_bdate(self.row.get('bdate'))
        self.university = int(self.row.get('university', 0))
        self.graduation = int(self.row.get('graduation', 0))
        self.faculty = int(self.row.get('faculty', 0))

    def _fill_bdate(self, bdate):
        if bdate is None:
            return
        items = bdate.split(".")
        if len(items) == 2:
            self.day, self.month = items
        elif len(items) == 3:
            self.day, self.month, self.year = items

    @property
    def date_str(self):
        return "{}.{}.{}".format(
            self.day or "?",
            self.month or "?",
            self.year or "?"
        )

    @property
    def in_NSU(self):
        return 671 == self.university

    @property
    def is_deactivated(self):
        return bool(self.row.get('deactivated', False))

    @property
    def vk_link(self):
        return format_html(
            "<a href='https://vk.com/id{}'>vk</a>".format(self.id)
        )

    def __str__(self):
        return "id{o.id}: {o.last_name} {o.first_name}".format(o=self)


class VkGroup(models.Model):
    row = JSONField()
    name = models.CharField(max_length=100)
    users = models.ManyToManyField(VkUser, related_name='groups')

    def _fill(self):
        self.id = self.row['id']
        self.name = self.row['name']

    def save(self, *args, **kwargs):
        self._fill()
        super().save(*args, **kwargs)

    def users_count(self):
        return self.users.count()


class VkPost(models.Model):
    post_id = models.IntegerField()
    row = JSONField()
    timestamp = models.IntegerField(null=True)
    owner_user = models.ForeignKey(VkUser, on_delete=models.CASCADE, null=True)
    owner_group = models.ForeignKey(VkGroup, on_delete=models.CASCADE, null=True)
    text = models.TextField()
    reposts = models.IntegerField()
    likes = models.IntegerField()
    source_data = JSONField()

    class Meta:
        unique_together = (('id', 'owner_user'), )

    @property
    def vk_link(self):
        return format_html(
            "<a href='https://vk.com/wall{}_{}'>vk</a>".format(
                self.owner_user.id,
                self.post_id
            )
        )

    @property
    def date(self):
        return datetime.fromtimestamp(self.timestamp)

    def save(self, *args, **kwargs):
        self._fill()
        self._find_source()
        self.find_user()
        super().save()

    def find_user(self):
        self.owner_user = VkUser.objects.get(id=self.row['owner_id'])

    def _fill(self):
        self.timestamp = self.row['date']
        self.post_id = self.row['id']
        self.text = self.row['text']
        self.reposts = self.row['reposts']['count']
        self.likes = self.row['likes']['count']

    def _find_source(self):
        # return None
        copy_history = self.row.get('copy_history', [{}])[0]
        self.source_data = {
            'owner_id': copy_history.get('owner_id'),
            'id': copy_history.get('id')
        }
