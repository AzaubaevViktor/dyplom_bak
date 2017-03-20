import pickle
import re

from my_nsu import parse_learn_info

obj = pickle.load(open("data.pckl", "rb"))

import itertools

parse_learn_info('выпускница группы 312 (1983г.), ММФ, специальность (1988 год выпуска)')

infos = []
for vv in obj.values():
    for v in vv:
        info = parse_learn_info(v)
        alumn = 'выпускн' in v.split(' ')[0]
        st = 'тудент' in v.split(' ')[0]

        if not (alumn or st):
            if info:
                infos.append(info)
            else:
                print("FUCK!!!")
                print(v)

keyvs = {}

for info in infos:
    for k, v in info.items():
        if not keyvs.get(k, None):
            keyvs[k] = set()
        keyvs[k].add(v)

from pprint import pprint
pprint(keyvs)

