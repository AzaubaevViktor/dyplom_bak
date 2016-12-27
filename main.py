import argparse
import json
import os

from mem_nr_db import MemNRDB, DBException

from vk_utils import VkInit, Group, get_users

APP_ID = os.environ['APP_ID']
APP_KEY = os.environ["APP_KEY"]
TOKEN_FILE = os.environ["TOKEN_FILE"]
SETTINGS = os.environ["SETTINGS"]
DB_FILE = os.environ["DB_FILE"]

vk_init = VkInit(APP_ID, TOKEN_FILE)
api = vk_init.api
print("Authorized with:")
print(api.users.get(user_ids=[0]))

print("Load settings...")
settings = json.loads(open(SETTINGS, "rt").read())
print("Ok")

try:
    db = MemNRDB.load(DB_FILE)
except DBException:
    db = MemNRDB()

t = db.init_table('users')


parser = argparse.ArgumentParser(
    description="Vk online grabber"
)

parser.add_argument("--delete-db", action='store_const', const=True, help="Delete DB file")
parser.add_argument("--load-from-groups", action='store_const', const=True, help="Update info from groups")
parser.add_argument("--online", action='store_const', const=True, help="Show online wall posts")

namespace = parser.parse_args()

if namespace.delete_db is None \
        and namespace.load_from_groups is None \
        and namespace.online is None:
    parser.print_help()
    exit()

if namespace.delete_db:
    print("Delete database")
    os.remove(DB_FILE)
    print("Complete")

if namespace.load_from_groups:
    print("Load user from groups")
    for group_name, cost in settings['groups'].items():
        group = Group(group_name)
        print("Group: {}".format(group_name))
        for ids in group.get_members(api):
            print("{} ids come".format(len(ids)))
            for user in get_users(api, ids):
                user.cost["group_{}".format(group_name)] = cost
                user.load_to_table(t)
            print("OK")
        print("Done! Saving...")
        db.serialize("db.json")
        print("Saved")

if namespace.online:
    print("Online mode")
    print(t)





