from django.core.paginator import Paginator


global COUNT_POST
COUNT_POST = 10


def get_paginator(post, request):
    paginator = Paginator(post, COUNT_POST)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return page_obj
