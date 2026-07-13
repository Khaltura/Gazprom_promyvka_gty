from django.shortcuts import redirect, render

from .forms import WashForm
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


def wash_create(request):
    if request.method == "POST":
        form = WashForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect("wash_list")
    else:
        form = WashForm()

    return render(
        request,
        "promyvki/wash_form.html",
        {"form": form},
    )