import json
import os

import time

import datetime

import logging

from mem_nr_db import MemNRDB, DBException, Query
from utils import Env, print_line
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

        self.users = self.db.init_table('users', convert=True, convert_exclude=["bdate"])

        self.log = logging.getLogger("Actions")

    def __call__(self, name):
        if "_" != name[0]:
            getattr(self, name)()
        else:
            print("Error: Action `{}` not found".format(name))

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
            total = 0
            for ids in group.get_members(self.api):
                print_line("Total: {}; {} users coming, processing... ".format(total, len(ids)))
                for user in self.api.get_users(ids):
                    user.cost["group_{}".format(group_name)] = cost
                    user.load_to(self.users)
                total += len(ids)
            print()
            print("Group {} done! Saving...".format(group_name))
            self.db.serialize("db.json")
            print("Saved")
        end = time.time()
        print("==========================")
        print("Total users in database: {}".format(len(self.users)))
        print("{:.2f} sec".format(end - start))
        print("Avg speed: {:.2f} users/sec".format(len(self.users) / (end- start)))

    def set_cost(self):
        print("Set costs to users")

        count = 0
        users_len = len(self.users)
        for user in self.users.rows(to_class=User):
            count += 1
            print_line("{}/{}: {}".format(count, users_len, str(user)))
            user_cost_setter(user)

    def online_mode(self):
        start = time.time()
        print("Online mode")
        print("===============================")
        user_count = 0
        users = []
        for user in self.users.rows(to_class=User):  # type: User
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


def user_cost_setter(user: User):
    user
