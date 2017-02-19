import pickle
import re

import time

obj = pickle.load(open("data.pckl", "rb"))


def parse_learn_info(s):
    original_s = s
    info = {}
    r_student = re.compile(r'(?:cтудент(ка)? группы (\d*[А-я]*)), ([А-я]*),')
    r_alumnus = re.compile(r'(?:выпускни(к|ца)? группы (\d*[А-я\- A-z]*)(?: (?:\()(\w*)г.(?:\)))?)(?: [СБМ])?, ([А-я]*),')
    r_other = re.compile(r'(профессор|доцент|ассистент|зав. кафедрой|почасовик|старший преподаватель|преподаватель) (\((Кафедра|Отделение) ([А-я\",\- ]*) ([А-я]+)\))?((?:\()([А-я ]*)(?:\)))?')
    r_outdate = re.compile(r'(?:\()(\d*) год выпуска(?:\))')
    r_second_degree = re.compile(r'второе высшее|2-ое высшее, ФГОС3+')
    r_braces = re.compile(r'(?:\()([А-я. ]*)(?:\))')

    # Обработка строчек 'студент...'
    student_info = alumni_info = other_info = {}
    student_info = r_student.findall(s)
    if not student_info:
        alumni_info = r_alumnus.findall(s)
        if not alumni_info:
            other_info = r_other.findall(s)

    if student_info:
        info['type'] = 'student'
        sex, group, faculty = student_info[0]
        s = re.sub(r_student, "", s)
        params = r_braces.findall(s)
        s = re.sub(r_braces, "", s)
        second = r_second_degree.findall(s)
        s = re.sub(r_second_degree, "", s)
        s = s.strip()
        if ',' == s[-1]:
            s = s[:-1]
        course = s

        info['sex'] = bool(sex)
        info['group'] = group
        info['faculty'] = faculty
        info['is_second'] = bool(second)
        info['course'] = course
        # parse params
        for param in params:
            if 'академ' in param:
                info['leave'] = True
            elif 'иностранн' in param:
                info['foreign'] = True
            elif 'ФИТ' in param:
                info['course'] += ' (ФИТ)'
            else:
                info['qualification'] = param

    if alumni_info:
        info['type'] = 'alumni'
        sex, group, indate, faculty = alumni_info[0]
        s = re.sub(r_alumnus, "", s)
        outdate = r_outdate.findall(s)
        s = re.sub(r_outdate, "", s)
        params = r_braces.findall(s)
        s = re.sub(r_braces, "", s)
        second = r_second_degree.findall(s)
        s = re.sub(r_second_degree, "", s)
        s = s.strip()
        if ',' == s[-1]:
            s = s[:-1]
        course = s

        info['sex'] = 1 == len(sex)
        info['group'] = group
        info['indate'] = indate
        info['outdate'] = outdate[0]
        info['faculty'] = faculty
        info['is_second'] = bool(second)
        info['course'] = course
        # parse params
        for param in params:
            if 'академ' in param:
                info['leave'] = True
            elif 'иностранн' in param:
                info['foreign'] = True
            elif 'ФИТ' in param:
                info['course'] += ' (ФИТ)'
            else:
                info['qualification'] = param

    if other_info:
        tp, _, train, what, faculty, _, other_train = other_info[0]
        info['type'] = tp
        info['train'] = train or other_train # Кафдера, отделение, etc
        info['train_what'] = what
        info['faculty'] = faculty

    return info

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

