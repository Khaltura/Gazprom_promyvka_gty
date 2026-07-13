from django.shortcuts import render
from django.db.models import Sum

from promyvki.models import CompressorStation, Wash
from .models import MaterialOperation


def balance_list(request):

    stations = []

    for station in CompressorStation.objects.all():

        # Приход
        arrival = (
            MaterialOperation.objects.filter(
                operation_type="arrival",
                to_station=station
            ).aggregate(total=Sum("amount"))["total"] or 0
        )

        # Списание
        writeoff = (
            MaterialOperation.objects.filter(
                operation_type="writeoff",
                from_station=station
            ).aggregate(total=Sum("amount"))["total"] or 0
        )

        # Расход на промывки
        wash = (
            Wash.objects.filter(
                station=station
            ).aggregate(total=Sum("cleaning_fluid_amount"))["total"] or 0
        )

        # Отдали другой КС
        transfer_out = (
            MaterialOperation.objects.filter(
                operation_type="transfer",
                from_station=station
            ).aggregate(total=Sum("amount"))["total"] or 0
        )

        # Получили от другой КС
        transfer_in = (
            MaterialOperation.objects.filter(
                operation_type="transfer",
                to_station=station
            ).aggregate(total=Sum("amount"))["total"] or 0
        )

        transfer = transfer_in - transfer_out

        balance = (
            arrival
            + transfer_in
            - transfer_out
            - writeoff
            - wash
        )

        stations.append({
            "name": station.name,
            "arrival": arrival,
            "wash": wash,
            "writeoff": writeoff,
            "transfer": transfer,
            "balance": balance,
        })

    total_balance = sum(s["balance"] for s in stations)

    return render(
        request,
        "balance/balance_list.html",
        {
            "stations": stations,
            "total_balance": total_balance,
        },
    )