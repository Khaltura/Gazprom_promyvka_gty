from decimal import Decimal

from django.db.models import Sum
from django.shortcuts import redirect, render

from promyvki.models import CompressorStation, CleaningFluid, Wash

from .forms import MaterialOperationForm
from .models import MaterialOperation


ZERO = Decimal("0.00")


def get_sum(queryset, field_name):
    """
    Возвращает сумму указанного поля.

    Если подходящих записей нет, возвращает Decimal("0.00").
    """
    result = queryset.aggregate(total=Sum(field_name))["total"]
    return result or ZERO


def balance_list(request):
    """
    Формирует таблицу баланса отдельно для каждой комбинации:

    компрессорная станция + промывочная жидкость.
    """
    balance_rows = []

    stations = CompressorStation.objects.all().order_by("name")
    fluids = CleaningFluid.objects.all().order_by("name")

    for station in stations:
        for fluid in fluids:

            # Приход жидкости на выбранную КС
            arrival = get_sum(
                MaterialOperation.objects.filter(
                    operation_type="arrival",
                    to_station=station,
                    cleaning_fluid=fluid,
                ),
                "amount",
            )

            # Списание неиспользованной жидкости
            writeoff = get_sum(
                MaterialOperation.objects.filter(
                    operation_type="writeoff",
                    from_station=station,
                    cleaning_fluid=fluid,
                ),
                "amount",
            )

            # Расход жидкости непосредственно на промывки
            wash = get_sum(
                Wash.objects.filter(
                    station=station,
                    cleaning_fluid=fluid,
                ),
                "cleaning_fluid_amount",
            )

            # Передано с текущей КС на другие станции
            transfer_out = get_sum(
                MaterialOperation.objects.filter(
                    operation_type="transfer",
                    from_station=station,
                    cleaning_fluid=fluid,
                ),
                "amount",
            )

            # Получено текущей КС от других станций
            transfer_in = get_sum(
                MaterialOperation.objects.filter(
                    operation_type="transfer",
                    to_station=station,
                    cleaning_fluid=fluid,
                ),
                "amount",
            )

            # Положительное значение означает, что КС получила больше,
            # чем передала. Отрицательное — передала больше, чем получила.
            transfer = transfer_in - transfer_out

            current_balance = (
                arrival
                + transfer_in
                - transfer_out
                - writeoff
                - wash
            )

            # Не показываем строки, по которым вообще не было движения.
            has_operations = any(
                value != ZERO
                for value in (
                    arrival,
                    writeoff,
                    wash,
                    transfer_in,
                    transfer_out,
                )
            )

            if has_operations:
                balance_rows.append(
                    {
                        "station": station,
                        "fluid": fluid,
                        "arrival": arrival,
                        "wash": wash,
                        "writeoff": writeoff,
                        "transfer_in": transfer_in,
                        "transfer_out": transfer_out,
                        "transfer": transfer,
                        "balance": current_balance,
                    }
                )

    total_balance = sum(
        (row["balance"] for row in balance_rows),
        ZERO,
    )

    return render(
        request,
        "balance/balance_list.html",
        {
            "balance_rows": balance_rows,
            "total_balance": total_balance,
        },
    )


def operation_create(request):
    """
    Создаёт приход, списание или перераспределение жидкости.

    После успешного сохранения возвращает пользователя
    на страницу баланса.
    """
    if request.method == "POST":
        form = MaterialOperationForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect("balance_list")
    else:
        form = MaterialOperationForm()

    return render(
        request,
        "balance/operation_form.html",
        {
            "form": form,
        },
    )