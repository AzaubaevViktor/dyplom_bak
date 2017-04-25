import abc
import datetime

import math

# Create your views here.
from typing import List, Tuple

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView

from lemmatize.models import Lemma, LemmaMeet
from lemmatize import processors


class BaseDataView(APIView, metaclass=abc.ABCMeta):
    fields = {}
    processors_list = tuple()

    def _fill(self, request):
        self.lemma = Lemma.objects.get(name=request.GET.get('word', 'сессия'))
        self.meets = LemmaMeet.objects.filter(lemma=self.lemma).order_by(
            "timestamp")

        self.kwargs = {}

        for field, (tp, default) in self.fields.items():
            val = tp(request.GET.get(field, default))
            self.kwargs[field] = val

    def _get_tss(self) -> List[int]:
        return [meet.timestamp for meet in self.meets]

    def get(self, request):
        self._fill(request)
        timestamps = self._get_tss()

        return Response(self._process(timestamps))

    def _process(self, timestamps: List[int]) -> List[Tuple[int, float]]:
        data = None
        for processor in self.processors_list[::-1]:
            data = processor(data or timestamps, **self.kwargs)

        return data


class Sliding(BaseDataView):
    fields = {
        'width': (int, "3600")
    }

    processors_list = [processors.sliding]


class SlidingDiff(Sliding):
    processors_list = [processors.diff_ranged, processors.sliding]


class SlidingDiffLog(Sliding):
    processors_list = [processors.limit, processors.diff_ranged, processors.sliding]


@api_view(["GET"])
def sliding(request):
    lemma = Lemma.objects.get(name=request.GET.get('word', 'сессия'))
    meets = LemmaMeet.objects.filter(lemma=lemma).order_by("timestamp")

    width = int(request.GET.get('width', 60 * 60))

    data = processors.sliding([meet.timestamp for meet in meets], width)

    return Response(data)


@api_view(['GET'])
def diff2(request):
    lemma = Lemma.objects.get(name=request.GET.get('word', 'сессия'))
    meets = LemmaMeet.objects.filter(lemma=lemma).order_by("timestamp")
    data = []

    meet_i = iter(meets)
    next(meet_i)
    meet = next(meet_i)
    prev_meet_i = iter(meets)
    prev_meet = next(prev_meet_i)

    try:
        while True:
            if meet.timestamp != prev_meet.timestamp:
                data.append((
                    meet.timestamp,
                    1 / math.log(meet.timestamp - prev_meet.timestamp)
                ))
            meet = next(meet_i)
            prev_meet = next(prev_meet_i)
    except StopIteration:
        pass

    return Response(data)


# @api_view(['GET'])
def diff(request):
    lemma = Lemma.objects.get(name=request.GET.get('word', 'сессия'))
    meets = LemmaMeet.objects.filter(lemma=lemma).order_by("timestamp")
    data = []

    count = 0
    cur_date = datetime.datetime.fromtimestamp(meets[0].timestamp).date()

    for meet in meets:
        date = datetime.datetime.fromtimestamp(meet.timestamp)
        if date.date() != cur_date:
            data.append((
                meet.timestamp,
                count
            ))
            count = 1
            cur_date = date.date()
        else:
            count += 1

    return Response(data)


class Source(BaseDataView):
    fields = {
        'width': (int, 3600)
    }
    processors_list = [processors.accumulation]


class SourceDiff(BaseDataView):
    fields = {
        'width': (int, 3600)
    }
    processors_list = [processors.diff_ranged, processors.accumulation]
