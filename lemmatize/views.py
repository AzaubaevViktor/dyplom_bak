from django.shortcuts import render

# Create your views here.
from .models import Lemma, LemmaMeet


def test(request):
    lemma = Lemma.objects.get(name='хуй')
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
    return render(request, 'test.html', {'data': data, 'lemma': lemma})
