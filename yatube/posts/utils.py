from django.core.paginator import Paginator
from django.conf import settings


def get_paginator(post, request):
    paginator = Paginator(post, settings.COUNT_POST)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return page_obj
