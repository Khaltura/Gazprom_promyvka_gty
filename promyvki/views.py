from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect, render

from users.utils import has_assigned_stations, user_stations

from .forms import WashForm
from .models import Wash


@login_required
def wash_list(request):
    if not has_assigned_stations(request.user):
        return redirect("account_pending")

    stations_all = user_stations(request.user)
    selected_station = None
    station_id = request.GET.get("station")
    if station_id:
        selected_station = stations_all.filter(pk=station_id).first()

    washes = Wash.objects.select_related(
        "station", "cleaning_fluid", "antifreeze", "created_by"
    ).filter(station__in=stations_all)

    if selected_station:
        washes = washes.filter(station=selected_station)

    return render(
        request,
        "promyvki/wash_list.html",
        {
            "washes": washes,
            "stations_all": stations_all,
            "selected_station": selected_station,
        },
    )


@login_required
def wash_create(request):
    if not has_assigned_stations(request.user):
        return redirect("account_pending")

    form = WashForm(request.POST or None, user=request.user)
    if request.method == "POST" and form.is_valid():
        wash = form.save(commit=False)
        wash.created_by = request.user
        wash.save()
        return redirect("wash_list")

    return render(request, "promyvki/wash_form.html", {"form": form, "wash": None})


@login_required
def wash_update(request, pk):
    wash = get_object_or_404(Wash, pk=pk)

    if not request.user.is_superuser:
        if wash.created_by_id != request.user.id:
            raise PermissionDenied("Вы можете редактировать только созданные вами промывки.")
        if not user_stations(request.user).filter(pk=wash.station_id).exists():
            raise PermissionDenied("Эта КС вам не назначена.")

    form = WashForm(request.POST or None, instance=wash, user=request.user)
    if request.method == "POST" and form.is_valid():
        updated_wash = form.save(commit=False)
        updated_wash.created_by = wash.created_by
        updated_wash.save()
        return redirect("wash_list")

    return render(request, "promyvki/wash_form.html", {"form": form, "wash": wash})
