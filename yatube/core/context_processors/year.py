import datetime


def year(request):
    """Добавляет переменную с текущим годом."""
    date = datetime.datetime.now().year
    return {'year': date}
