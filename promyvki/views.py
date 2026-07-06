from django.shortcuts import render

from .models import Wash


def wash_list(request):
    washes = Wash.objects.select_related(
        "station",
        "cleaning_fluid",
        "antifreeze",
    ).order_by("-date")

    return render(
        request,
        "promyvki/wash_list.html",
        {"washes": washes},
    )