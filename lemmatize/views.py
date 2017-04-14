import datetime

import math

from django.db.models import Count
from django.http import HttpResponse
from django.shortcuts import render

# Create your views here.

from .models import Lemma, LemmaMeet


def max_list(request):
    count = request.GET.get('count', 100)
    lemmas = Lemma.objects.annotate(_meets_count=Count('meets')).filter(_meets_count__gte=count).all()

    i = 0

    data = []

    for lemma in lemmas:
        data.append((lemma.name, lemma.meets_count))

    data.sort(key=lambda x: x[1])

    return HttpResponse(str(data))



def sliding(request):
    lemma = Lemma.objects.get(name=request.GET.get('word', 'сессия'))
    meets = LemmaMeet.objects.filter(lemma=lemma).order_by("timestamp")
    data = "["

    width = int(request.GET.get('width', 60 * 60))

    left = 0
    left_ts = meets[0].timestamp
    right = 0

    for i, meet in enumerate(meets):
        if meet.timestamp - meets[0].timestamp < width:
            right = i
        else:
            break

    data += "[{}, {}], ".format(left_ts + width / 2, right - left)

    while right + 1 < len(meets):
        if meets[right + 1].timestamp - (left_ts + width) < meets[left + 1].timestamp - left_ts:
            right += 1
            left_ts = meets[right].timestamp - width
        else:
            left += 1
            left_ts = meets[left].timestamp

        data += "[{}, {}], ".format(left_ts + width / 2, right - left)

    data += "]"

    return render(request, 'graph.html', {'data': data, 'lemma': lemma})


def diff2(request):
    lemma = Lemma.objects.get(name='посвяга')
    meets = LemmaMeet.objects.filter(lemma=lemma).order_by("timestamp")
    data = "["

    meet_i = iter(meets)
    next(meet_i)
    meet = next(meet_i)
    prev_meet_i = iter(meets)
    prev_meet = next(prev_meet_i)

    try:
        while True:
            if meet.timestamp != prev_meet.timestamp:
                data += "[{}, {}], ".format(
                    meet.timestamp,
                    1 / math.log(meet.timestamp - prev_meet.timestamp)
                )
            meet = next(meet_i)
            prev_meet = next(prev_meet_i)
    except StopIteration:
        data += "]"

    return render(request, 'graph.html', {'data': data, 'lemma': lemma})




def diff(request):
    lemma = Lemma.objects.get(name='хуй')
    meets = LemmaMeet.objects.filter(lemma=lemma).order_by("timestamp")
    data = "["

    count = 0
    cur_date = datetime.datetime.fromtimestamp(meets[0].timestamp).date()

    for meet in meets:
        date = datetime.datetime.fromtimestamp(meet.timestamp)
        if date.date() != cur_date:
            data += "[{}, {}], ".format(
                meet.timestamp,
                count
            )
            count = 1
            cur_date = date.date()
        else:
            count += 1

    data += "]"
    return render(request, 'graph.html', {'data': data, 'lemma': lemma})



def graph(request):
    lemma = Lemma.objects.get(name=request.GET.get('word', 'сессия'))
    meets = LemmaMeet.objects.filter(lemma=lemma).order_by("timestamp")
    data = "["
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
            data += "[{},{}],".format(meet.timestamp,
                                      count,
                                      # 1/(meet.timestamp - prev_meet.timestamp)
                                      )

            meet = next(meet_i)
            prev_meet = next(prev_meet_i)
    except StopIteration:
        pass

    data += "]"
    return render(request, 'graph.html', {'data': data, 'lemma': lemma})

