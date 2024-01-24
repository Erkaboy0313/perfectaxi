from django.urls import path
from .click import *

urlpatterns = [
    path('click/prepare/',prepare, name = 'prepare'),
    path('click/complate/',complete, name = 'complete'),
]