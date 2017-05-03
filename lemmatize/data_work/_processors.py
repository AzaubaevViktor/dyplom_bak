import abc
from enum import Enum
from math import pi
from typing import List, Tuple, Iterable, Type, Callable

import itertools

import math

from lemmatize.models import Lemma, LemmaMeet
from ._types import DataEntry, Argument


processors = {}  # type: List[Type[DataProcessor]]


def register(Class):
    processors[Class.__name__] = Class
    return Class


class DataProcessorError(Exception):
    def __init__(self, processor: 'DataProcessor', text: str):
        self.processor = processor
        self.text = text

    def __str__(self):
        return "Во время выполнения `{}` возникла ошибка `{}`".format(
            self.processor.name,
            self.text
        )


class DataProcessor(metaclass=abc.ABCMeta):
    name = "Abstract processor"
    desc = 'Short description'
    args = ()  # type: Tuple[Argument]

    def __init__(self, source: 'DataProcessor', *args, **kwargs):
        self.source = source
        self._parse_args(**kwargs)

    def _parse_args(self, **kwargs):
        for name, desc, _type in self.args:
            value = _type(kwargs[name])
            setattr(self, name, value)

    @abc.abstractmethod
    def __iter__(self) -> Iterable[DataEntry]:
        pass

    def pared_iter(self) -> Iterable[Tuple[DataEntry, DataEntry]]:
        prev = None
        for entry in iter(self):
            if prev is not None:
                yield prev, entry
            prev = entry

    @abc.abstractmethod
    def __len__(self) -> int:
        pass

    def __str__(self):
        return "Source<{}>".format(self.name)


@register
class LemmaMeetSource(DataProcessor):
    name = "Данные из БД"
    desc = "Берёт встречи лемм из БД"
    args = (('lemma_name', 'Слово', str),)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.source is not None:
            raise DataProcessorError(self,
                                     'Данный источник может быть только первым')

        self._lemma = Lemma.objects.get(name=self.lemma_name)
        self._meets = LemmaMeet.objects.filter(lemma=self._lemma).order_by(
            "timestamp")
        self._len = self._meets.count()

    def __iter__(self) -> Iterable[DataEntry]:
        for meet in self._meets:
            yield meet.timestamp, 1

    def __len__(self) -> int:
        return self._len


@register
class Accumulation(DataProcessor):
    name = "Кумулятивный"
    desc = "Собирает кумулятивный график"

    def __iter__(self) -> Iterable[DataEntry]:
        count = 0
        for cur in iter(self.source):
            count += cur[1]

            yield cur[0], count

    def __len__(self):
        return len(self.source)


@register
class Diff(DataProcessor):
    name = "Производная"
    desc = "Считается производная"

    def __iter__(self) -> Iterable[DataEntry]:
        prev_ts = 0
        for prev, cur in self.source.pared_iter():
            if prev[0] != cur[0]:
                prev_ts = prev[0]
                yield (cur[0] + prev_ts) / 2, \
                      (cur[1] - prev[1]) / (cur[0] - prev_ts)

    def __len__(self):
        return len(self.source) - 1


@register
class Sliding(DataProcessor):
    name = "Скользящее окно"
    desc = "Скользящее окно"
    args = (
        ('width', 'Ширина окна (сек)', int),
        ('steps', 'Количество отсчётов', int),
        ('function', 'Функция', int)
    )

    functions = ["_linear", "_wtf", "_normal"]

    def __init__(self, source: 'DataProcessor', *args, **kwargs):
        super().__init__(source, *args, **kwargs)
        self.width2 = self.width / 2
        self.step = self.width / self.steps
        self.function = self.function or 0

    @property
    def _f(self) -> Callable:
        return getattr(self,
                       self.functions[self.function],
                       )

    def _linear(self, point: float, x: float):
        """ Функция для учитывания окна """

        v = abs(point - x) / self.width2

        return 1 - min(v, 1)

    def _wtf(self, point: float, x: float):
        v = (x - point) / self.width2
        if abs(v) > 1:
            return 0
        else:
            return v

    def _normal(self, point: float, x: float):
        # e ^ (-x ^ 2 / 0.4) / 0.4 / root(2 * pi, 2)
        _x = (point - x) / self.width2
        if abs(_x) > 1:
            return 0
        _x2 = _x * _x

        return math.e ** (-_x2 / 0.4)

    def __iter__(self):
        cache = [0] * self.steps
        si = iter(self.source)

        ts1, val1 = next(si)

        start_ts = ts1 - self.width2
        cur_step = 0

        for ts, val in itertools.chain([(ts1, val1)], si):
            while start_ts + cur_step * self.step < ts - self.width2:
                yield start_ts + cur_step * self.step, cache.pop(0)
                cache.append(0)
                cur_step += 1

            for s in range(cur_step, cur_step + self.steps):
                cache[s - cur_step] += \
                    val * self._f(start_ts + s * self.step, ts)

        for i, v in enumerate(cache):
            yield start_ts + (cur_step + i) * self.step, v

    def __len__(self):
        pass


def accumulation(timestamps: List[int], **kwargs) -> List[Tuple[int, int]]:
    count = 0
    data = []

    ts_i = iter(timestamps)
    ts = next(ts_i)
    prev_ts_i = iter(timestamps)

    width = kwargs.get("width", 60 * 60)

    try:
        while True:
            ts = next(ts_i)
            prev_ts = next(prev_ts_i)

            if ts - prev_ts > width:
                data.append((ts, count))

            count += 1

    except StopIteration:
        data.append((ts, count))

    return data


def sliding(timestamps: List[int], width=3600, **kwargs) -> List[Tuple[int, int]]:
    """
    
    :param timestamps: список исходных timestamp-ов
    :param width: ширина окна сдвига
    :return: 
    """
    data = []

    left = 0
    left_ts = timestamps[0]
    right = 0

    for i, ts in enumerate(timestamps):
        if ts - timestamps[0] < width:
            right = i
        else:
            break

    data.append((left_ts + width / 2, right - left))

    while right + 1 < len(timestamps):
        if timestamps[right + 1] - (left_ts + width) < timestamps[left + 1] - left_ts:
            right += 1
            left_ts = timestamps[right] - width
        else:
            left += 1
            left_ts = timestamps[left]

        data.append((left_ts + width / 2, right - left))

    return data


def _approx(p: Tuple[int, float], n: Tuple[int, float], c: int) -> Tuple[int, float]:
    return c, p[1] + (n[1] - p[1]) / (n[0] - p[0]) * (c - p[0])


def fixed(timestamps: List[Tuple[int, float]], dx=3600, **kwargs) -> List[Tuple[int, int]]:
    data = []

    prev_i = iter(timestamps)
    cur_i = iter(timestamps)
    cts, cv = next(cur_i)  # start

    try:
        while True:
            pts, pv = next(prev_i)
            nts, nv = next(cur_i)
            while cts < nts:

                data.append(
                    _approx((pts, pv), (nts, nv), cts)
                )
                cts += dx

    except StopIteration:
        pass

    return data


def diff_ranged(ts_val: List[Tuple[int, float]], **kwargs) -> List[Tuple[int, float]]:
    data = []

    width = kwargs.get('width', 60 * 60)

    prev_v = 0
    prev_ts = ts_val[0][0]

    for ts, v in ts_val:
        if ts - prev_ts > width:
            data.append((
                (ts + prev_ts) / 2,
                (v - prev_v) / (ts - prev_ts)
            ))
            prev_ts = ts
            prev_v = v

    return data


def limit(ts_val: List[Tuple[int, int]], **kwargs) -> List[Tuple[int, float]]:
    data = []

    positive = [i[1] for i in ts_val if i[1] > 0]
    avg_p = sum(positive) / len(positive)

    negative = [i[1] for i in ts_val if i[1] < 0]
    avg_n = sum(negative) / len(negative)

    for ts, v in ts_val:
        if v > 0:
            v = min((v, avg_p))
        else:
            v = max((v, avg_n))

        data.append((ts, v))

    return data


def exp_smooth(ts_val: List[Tuple[int, int]], **kwargs) -> List[Tuple[int, float]]:
    data = []

    alpha = kwargs.get('alpha', 0.7)

    cur_ts, val_es = ts_val[0]

    for ts, val in ts_val:
        val_es = alpha * val + (1 - alpha) * val_es

        data.append((ts, val_es))

    return data


def weigth_avg(ts_val: List[Tuple[int, int]], **kwargs) -> List[Tuple[int, float]]:
    data = []

    alpha = kwargs.get('alpha', 0.3)
    last = 60 * 60 * 24

    cur_ts, val_es = ts_val[0]

    for ts, val in ts_val:
        if ts != cur_ts:
            b = min(alpha * last / (ts - cur_ts), 1)  # неправильно

            val_es = b * val + (1 - b) * val_es
            cur_ts = ts

            data.append((ts, val_es))

    return data