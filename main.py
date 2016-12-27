import json
import os

from mem_nr_db import MemNRDB

from vk_utils import VkInit, Group, get_users

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

db = MemNRDB()
t = db.create_table('users')

for group_name, cost in settings['groups'].items():
    group = Group(group_name)
    print(group_name)
    for ids in group.get_members(api):
        print("{} ids come".format(len(ids)))
        for user in get_users(api, ids):
            user.cost += cost
            user.load_to_table(t)
        print("Done!")

    db.serialize("db.json")

pass
print(t)




