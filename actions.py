import json
import os

import time

import datetime

import logging

from mem_nr_db import MemNRDB, DBException, Query
from utils import Env
from vk_utils import VkInit, Group, User


class Actions:
    def __init__(self):
        vk_init = VkInit(Env.APP_ID, Env.TOKEN_FILE)
        self.api = vk_init.api

        print("Authorized with:")
        print(self.api.users.get(user_ids=[0]))

        print("Load settings...")
        self.settings = json.loads(open(Env.SETTINGS, "rt").read())
        print("Ok")

        try:
            self.db = MemNRDB.load(Env.DB_FILE)
        except FileNotFoundError:
            self.db = MemNRDB()

        self.users = self.db.init_table('users')

        self.log = logging.getLogger("Actions")

    def __call__(self, name):
        if "__" not in name:
            getattr(self, name)()
        else:
            print("action `{}` not found".format(name))

    @staticmethod
    def delete_db():
        print("Delete database")
        os.remove(Env.DB_FILE)
        print("Complete")

    def load_from_groups(self):
        print("Load user from groups")
        start = time.time()
        for group_name, cost in self.settings['groups'].items():
            group = Group(group_name)
            print("Group: {}".format(group_name))
            for ids in group.get_members(self.api):
                print("{} users coming, processing... ".format(len(ids)), end='')
                for user in self.api.get_users(ids):
                    user.cost["group_{}".format(group_name)] = cost
                    user.load_to(self.users)
                print("OK")
            print("Group {} done! Saving...".format(group_name))
            self.db.serialize("db.json")
            print("Saved")
        end = time.time()
        print("{} sec".format(end - start))

    def online_mode(self):
        start = time.time()
        print("Online mode")
        print("===============================")
        user_count = 0
        users = []
        for user in self.users.query(Query.ANY()).all(to_class=User):  # type: User
            user_count += 1
            users.append(user)
            if 25 == len(users):
                for cur_user, dt, text, likes, reposts in self.api.get_wall_posts(users, 2, start):
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
                self.log.debug("{} by {:.2f} sec, {:.2f} user/sec ({}...{})".format(
                    user_count,
                    time.time() - start,
                    user_count / (time.time() - start),
                    users[0],
                    users[-1]
                ))

                # time.sleep(1)
                users = []

