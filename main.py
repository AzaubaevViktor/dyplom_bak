import json
import os

from vk_utils import VkInit, Group

APP_ID = os.environ['APP_ID']
APP_KEY = os.environ["APP_KEY"]
TOKEN_FILE = os.environ["TOKEN_FILE"]
SETTINGS = os.environ["SETTINGS"]

vk_init = VkInit(APP_ID, TOKEN_FILE)
api = vk_init.api
print("Authorized with:")
print(api.users.get(user_ids=[0]))

print("Load settings...")

settings = json.loads(open(SETTINGS, "rt").read())

for group_name, cost in settings['groups'].items():
    group = Group(group_name)
    for _id in group.get_members(api):
        pass


