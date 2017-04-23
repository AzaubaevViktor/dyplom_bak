import datetime

import math

from django.db.models import Count
from django.http import HttpResponse
from django.shortcuts import render

# Create your views here.
from rest_framework.decorators import api_view
from rest_framework.response import Response

from lemmatize.models import Lemma, LemmaMeet


@api_view(["GET"])
def sliding(request):
    lemma = Lemma.objects.get(name=request.GET.get('word', 'сессия'))
    meets = LemmaMeet.objects.filter(lemma=lemma).order_by("timestamp")
    data = []

    width = int(request.GET.get('width', 60 * 60))

    left = 0
    left_ts = meets[0].timestamp
    right = 0

    for i, meet in enumerate(meets):
        if meet.timestamp - meets[0].timestamp < width:
            right = i
        else:
            break

    data.append((left_ts + width / 2, right - left))

    while right + 1 < len(meets):
        if meets[right + 1].timestamp - (left_ts + width) < meets[left + 1].timestamp - left_ts:
            right += 1
            left_ts = meets[right].timestamp - width
        else:
            left += 1
            left_ts = meets[left].timestamp

        data.append((left_ts + width / 2, right - left))

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


@api_view(['GET'])
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


@api_view(['GET'])
def source(request):
    lemma = Lemma.objects.get(name=request.GET.get('word', 'сессия'))
    meets = LemmaMeet.objects.filter(lemma=lemma).order_by("timestamp")
    data = []
    count = 0

    meet_i = iter(meets)
    next(meet_i)
    meet = next(meet_i)
    prev_meet_i = iter(meets)
    prev_meet = next(prev_meet_i)

    try:
        while True:
            count += 1
            # if meet.timestamp != prev_meet.timestamp:
            data.append((meet.timestamp, count))

            meet = next(meet_i)
            prev_meet = next(prev_meet_i)
    except StopIteration:
        pass

    return Response(data)
