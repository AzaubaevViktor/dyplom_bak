from django.contrib.postgres.fields import JSONField
from django.db import models
import random

# Create your models here.


class VkConnector(models.Model):
    app_id = models.CharField(max_length=50)
    _token = models.CharField(max_length=200)

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
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    _bdate = models.CharField(max_length=20)
    bdate = models.DateField()
    university = models.IntegerField(default=0)
    graduation = models.IntegerField(default=0)
    twitter = models.CharField(max_length=70)

    def __init__(self, row, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.id = row['id']
        self.row = row
        self._fill()

    def _fill(self):
        self.sex = int(self.row['sex'])
        self.first_name = self.row['first_name']
        self.last_name = self.row['last_name']
        self._bdate = self.row.get('bdate')
        self.university = int(self.row.get('university', 0))
        self.graduation = int(self.row.get('graduation', 0))

    @property
    def in_NSU(self):
        return 671 == self.university


class VkGroup(models.Model):
    users = models.ManyToManyField(VkUser, related_name='groups')


class VkPost(models.Model):
    row = JSONField()
    _date = models.IntegerField()
    date = models.DateField()
    owner_user = models.ForeignKey(VkUser, on_delete=models.CASCADE)
    owner_group = models.ForeignKey(VkGroup, on_delete=models.CASCADE)
    text = models.TextField()
    reposts = models.IntegerField()
    likes = models.IntegerField()
    source = models.ForeignKey('VkPost')

    def __init__(self, row, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.id = row['id']
        self.row = row
        self._fill()
        self._find_source()

    def find_user(self):
        self.owner_user = VkUser.objects.get(self.row['owner_id'])

    def _fill(self):
        self._date = self.row['date']
        self.id = self.row['id']
        self.text = self.row['text']
        self.reposts = self.row['reposts']['count']
        self.likes = self.row['likes']['count']

    def _find_source(self):
        return None
        copy_history = self.row.get('copy_history', {})
        self.source = {
            'owner_id': copy_history.get('owner_id'),
            'id': copy_history.get('id')
        }