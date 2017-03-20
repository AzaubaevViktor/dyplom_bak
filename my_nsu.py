import re


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


class Person:
    def __init__(self, _id):
        self.id = _id
        self.url = 'http://my.nsu.ru/public/studentinfo.jsp?public.studentinfo.ref={}'.format(_id)
        self.parsers = {
            'info': self.parser_person_info,
            'photo': self.parser_person_photo
        }

    def parser_person_info(self, div):
        data = {}
        # Get Name and brithday
        text = div.find('h2').text.strip()
        i = text.find('(')

        if -1 != i:
            data['name'] = text[:i].strip().split(" ")
            data['birthday'] = text[i:][1:-1]
        else:
            data['name'] = text.strip()

        # Get line about learn
        data['learn'] = []
        for li in div.xpath("ul/li"):
            s = " ".join([x.strip() for x in li.text_content().split(" ") if x.strip()])
            data['learn'].append(parse_learn_info(s) or s)

        return data

    def parser_person_photo(self, div):
        return "http://my.nsu.ru" + div.find("img").attrib['src']

    def parse(self):
        raw_data = self._get_raw_data()
        data = {}
        for key, div in raw_data.items():
            parser = self.parsers.get(key, lambda b: {})
            result = parser(div)
            data[key] = result
        return data

    def _get_raw_data(self):
        try:
            root = html.parse(self.url).getroot()
        except OSError:
            return {}

        content = root.get_element_by_id('content')
        divs = content.xpath('div[contains(@class, "person-")]')
        person = {}
        for div in divs:
            person[div.attrib['class'].split('-')[1]] = div
        return person
