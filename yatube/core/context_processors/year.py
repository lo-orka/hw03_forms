import datetime

def year(request):
    """Добавляет переменную с текущим годом."""
    date = datetime.datetime.now().year
    date = int(date)
    return {
           'year': date
    }