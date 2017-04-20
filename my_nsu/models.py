import re

from django.contrib.postgres.fields import ArrayField
from django.db import models

# Create your models here.
from lxml import html


class MyNsuUserManager(models.Manager):
    url_fmt = 'http://my.nsu.ru/public/studentinfo.jsp?public.studentinfo.ref={}'

    def get_from_site(self, _id):
        url = self.url_fmt.format(_id)
        raw_data = self._get_raw_data(url)
        if raw_data is None:
            return None
        info = self._parser_person_info(raw_data)
        first, last, patron = self._parse_name(info['name'])

        if len(info['learn']) == 0:
            info['learn'] = [{}]

        return self.create(
            id=_id,
            first_name=first,
            last_name=last,
            patronymic=patron,
            **info['learn'][0]
        )

    def _parse_name(self, full_name: str):
        items = full_name.split(" ")
        if len(items) == 2:
            return (*items, "")
        if len(items) == 3:
            return items
        return "", "", ""

    def _get_raw_data(self, url):
        try:
            root = html.parse(url).getroot()
        except OSError:
            return None

        content = root.get_element_by_id('content')
        divs = content.xpath('div[contains(@class, "person-")]')
        person = {}
        for div in divs:
            person[div.attrib['class'].split('-')[1]] = div
        return person.get('info', None)

    def _parser_person_info(self, div):
        data = {}
        # Get Name and brithday
        text = div.find('h2').text.strip()
        i = text.find('(')

        if -1 != i:
            data['name'] = text[:i].strip()
            data['birthday'] = text[i:][1:-1]
        else:
            data['name'] = text.strip()

        # Get line about learn
        data['learn'] = []
        for li in div.xpath("ul/li"):
            s = " ".join([x.strip() for x in li.text_content().split(" ") if x.strip()])
            data['learn'].append(self._parse_learn_info(s))

        return data

    def _parse_learn_info(self, s):
        original_s = s
        info = {'source': original_s}
        r_student = re.compile(r'(?:cтудент(ка)? группы (\d*[А-я]*)), ([А-я]*),')
        r_second_degree = re.compile(r'второе высшее|2-ое высшее, ФГОС3+')
        r_braces = re.compile(r'(?:\()([А-я. ]*)(?:\))')

        # Обработка строчек 'студент...'
        student_info = alumni_info = other_info = {}
        student_info = r_student.findall(s)
        if not student_info:
            return {}

        if student_info:
            info['user_type'] = 'student'
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
            # info['is_second'] = bool(second)
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
        else:
            return {}

        return info


class MyNsuUser(models.Model):
    SEX = (
        (0, 'Unknown'),
        (1, 'Woman'),
        (2, 'Man')
    )

    source = models.CharField(max_length=300)

    first_name = models.CharField(max_length=100, default="")
    last_name = models.CharField(max_length=100, default="")
    patronymic = models.CharField(max_length=100, default="")

    sex = models.SmallIntegerField(choices=SEX, null=True)
    group = models.CharField(max_length=20, null=True)
    faculty = models.CharField(max_length=20, null=True)
    course = models.CharField(max_length=200, null=True)
    user_type = models.CharField(max_length=80, null=True)
    leave = models.BooleanField(default=False)
    foreign = models.BooleanField(default=False)
    qualification = models.CharField(max_length=80, null=True)

    objects = MyNsuUserManager()

    def __str__(self):
        return "MyNsuUser<{} {}, {}, {}>".format(
            self.first_name,
            self.last_name,
            self.faculty,
            self.group
        )
