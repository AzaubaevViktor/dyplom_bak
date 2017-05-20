from django.shortcuts import render


def main(request):
    pass


def load_state(request):
    return render(request, 'index.html')


def word(request):
    return render(request, "word.html")

def words(request):
    return render(request, "words.html")

def settings(request):
    return render(request, "settings.html")
