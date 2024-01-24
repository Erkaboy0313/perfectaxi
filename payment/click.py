from django.views.decorators.csrf import csrf_exempt
from . import click_utils

@csrf_exempt
def prepare(request):
    return click_utils.prepare(request)

@csrf_exempt
def complete(request):
    return click_utils.complete(request)
