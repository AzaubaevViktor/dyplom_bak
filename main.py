import os

from vk_utils import VkInit

APP_ID = os.environ['APP_ID']
APP_KEY = os.environ["APP_KEY"]
TOKEN_FILE = os.environ["TOKEN_FILE"]

vk_init = VkInit(APP_ID, TOKEN_FILE)
api = vk_init.api
print(api.users.get(user_ids=[0]))


