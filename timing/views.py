from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response

from vkontakte.models import VkPost


def main(request):
    return render(request, "timing/base.html")


@api_view(['GET'])
def times(request):
    posts = VkPost.objects.order_by('timestamp')[:1000]

    data = []
    day = 60 * 60 * 24

    for post in posts:
        data.append((
            int(post.timestamp // day),
            int(post.timestamp % day),
            0
        ))

    return Response(data)

