from django.shortcuts import render
import logging


def index(request):
    logging.debug("Hello World")
    return render(request, 'fdmanager/index.html', None)
