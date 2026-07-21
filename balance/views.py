from decimal import Decimal

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db import models
from django.db.models import Sum
from django.shortcuts import get_object_or_404, redirect, render

from promyvki.models import Antifreeze, CleaningFluid, CompressorStation, Wash

from .forms import MaterialOperationForm
from .models import MaterialOperation
from users.utils import has_assigned_stations, user_stations

ZERO = Decimal("0.00")


def station_scope(user):
    return user_stations(user)


def selected_station_scope(request):
    """Возвращает доступные КС с учётом выбранного фильтра."""
    available = station_scope(request.user)
    selected = None
    station_id = request.GET.get("station")
    if station_id:
        selected = available.filter(pk=station_id).first()
        if selected:
            return available.filter(pk=selected.pk), available, selected
    return available, available, selected


def sum_field(queryset, field="amount"):
    return queryset.aggregate(value=Sum(field))["value"] or ZERO


def build_row(station, material_type, material):
    key = "cleaning_fluid" if material_type == MaterialOperation.CLEANING else "antifreeze"
    base = MaterialOperation.objects.filter(material_type=material_type, **{key: material})

    arrival = sum_field(base.filter(operation_type=MaterialOperation.ARRIVAL, to_station=station))
    writeoff = sum_field(base.filter(operation_type=MaterialOperation.WRITEOFF, from_station=station))
    incoming = sum_field(base.filter(operation_type=MaterialOperation.TRANSFER, to_station=station))
    outgoing = sum_field(base.filter(operation_type=MaterialOperation.TRANSFER, from_station=station))

    if material_type == MaterialOperation.CLEANING:
        consumed = sum_field(
            Wash.objects.filter(station=station, cleaning_fluid=material),
            "cleaning_fluid_amount",
        )
    else:
        consumed = sum_field(
            Wash.objects.filter(station=station, antifreeze=material),
            "antifreeze_amount",
        )

    balance = arrival + incoming - outgoing - writeoff - consumed
    return {
        "station": station,
        "material_type": material_type,
        "material_type_label": dict(MaterialOperation.MATERIAL_TYPES)[material_type],
        "material": material,
        "arrival": arrival,
        "writeoff": writeoff,
        "transfer_in": incoming,
        "transfer_out": outgoing,
        "transfer": incoming - outgoing,
        "wash": consumed,
        "balance": balance,
        "active": any(
            value != ZERO for value in (arrival, writeoff, incoming, outgoing, consumed)
        ),
    }


def operation_scope(user):
    operations = MaterialOperation.objects.select_related(
        "from_station", "to_station", "cleaning_fluid", "antifreeze", "created_by"
    )
    if user.is_superuser:
        return operations
    stations = user_stations(user)
    if not stations.exists():
        return operations.none()
    return operations.filter(
        models.Q(from_station__in=stations) | models.Q(to_station__in=stations)
    ).distinct()


@login_required
def balance_list(request):
    if not has_assigned_stations(request.user):
        return redirect("account_pending")

    rows = []
    stations, stations_all, selected_station = selected_station_scope(request)

    for station in stations:
        for fluid in CleaningFluid.objects.all():
            row = build_row(station, MaterialOperation.CLEANING, fluid)
            if row["active"]:
                rows.append(row)

        for antifreeze in Antifreeze.objects.all():
            row = build_row(station, MaterialOperation.ANTIFREEZE, antifreeze)
            if row["active"]:
                rows.append(row)

    grouped = []
    for material_type, queryset in (
        (MaterialOperation.CLEANING, CleaningFluid.objects.all()),
        (MaterialOperation.ANTIFREEZE, Antifreeze.objects.all()),
    ):
        for material in queryset:
            material_rows = [
                row
                for row in rows
                if row["material_type"] == material_type and row["material"] == material
            ]
            if material_rows:
                grouped.append(
                    {
                        "material_type_label": dict(MaterialOperation.MATERIAL_TYPES)[material_type],
                        "material": material,
                        "balance": sum((row["balance"] for row in material_rows), ZERO),
                    }
                )

    operations = operation_scope(request.user)
    if selected_station:
        operations = operations.filter(
            models.Q(from_station=selected_station) | models.Q(to_station=selected_station)
        ).distinct()

    return render(
        request,
        "balance/balance_list.html",
        {
            "balance_rows": rows,
            "material_summary": grouped,
            "operations": operations,
            "stations_all": stations_all,
            "selected_station": selected_station,
        },
    )


@login_required
def operation_create(request):
    if not has_assigned_stations(request.user):
        return redirect("account_pending")

    form = MaterialOperationForm(request.POST or None, user=request.user)
    if request.method == "POST" and form.is_valid():
        operation = form.save(commit=False)
        operation.created_by = request.user
        operation.save()
        return redirect("balance_list")

    return render(
        request,
        "balance/operation_form.html",
        {"form": form, "operation": None},
    )


@login_required
def operation_update(request, pk):
    operation = get_object_or_404(MaterialOperation, pk=pk)

    if not request.user.is_superuser and operation.created_by_id != request.user.id:
        raise PermissionDenied("Вы можете редактировать только созданные вами операции.")

    form = MaterialOperationForm(
        request.POST or None,
        instance=operation,
        user=request.user,
    )
    if request.method == "POST" and form.is_valid():
        updated_operation = form.save(commit=False)
        updated_operation.created_by = operation.created_by
        updated_operation.save()
        return redirect("balance_list")

    return render(
        request,
        "balance/operation_form.html",
        {"form": form, "operation": operation},
    )


@login_required
def operation_list(request):
    # Старый адрес оставлен для совместимости, отдельного журнала больше нет.
    return redirect("balance_list")
