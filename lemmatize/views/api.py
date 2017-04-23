from rest_framework import views
from rest_framework.response import Response
from django.db.models import Count

from lemmatize.models import Lemma
from lemmatize.serializers import LemmaSerializer


class LemmaSearch(views.APIView):
    def get(self, request, name, format=None):
        count = request.GET.get('count', 10)
        resp_id = request.GET.get('resp_id', 0)

        lemmas = Lemma.objects.filter(name__contains=name) \
                     .annotate(_meets_count=Count('meets')) \
                     .order_by('-_meets_count')[:count]
        data = [s.data for s in map(LemmaSerializer, lemmas)]

        return Response({
            'lemmas': data,
            'resp_id': resp_id
        })

