import argparse
import datetime
import json
import os
import sys

import time

from mem_nr_db import MemNRDB, DBException, Query

from vk_utils import VkInit, Group, get_users, User, get_wall_posts

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
                user.load_to(t)
            print("OK")
        print("Done! Saving...")
        db.serialize("db.json")
        print("Saved")

start = time.time()
if namespace.online:
    print("Online mode")
    print("===============================")
    user_count = 0
    users = []
    for user in t.query(Query.ANY()).all(to_class=User):  # type: User
        user_count += 1
        users.append(user)
        if 25 == len(users):
            for cur_user, dt, text, likes, reposts in get_wall_posts(api, users, 2, start):
                print("{}:".format(str(cur_user)))
                print(" {}; {}/{}".format(
                    datetime.datetime.fromtimestamp(
                        int(dt)
                    ).strftime('%d.%m.%Y %H:%M:%S'),
                    likes,
                    reposts
                ))
                print(" {}".format(text))
                print("-------------------------------")
            print("{} by {} sec, {} user/sec (last_id:{})".format(
                user_count,
                time.time() - start,
                user_count / (time.time() - start),
                users[-1]
            ))

            # time.sleep(1)
            users = []

