import gspread
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_POST
from oauth2client.service_account import ServiceAccountCredentials

from trello_spreadsheets_django.consts import google_config


def index(request):
    return render(request, 'index.html')


@require_POST
def create_table(request):
    table_name = request.POST.get('table')
    company_name = request.POST.get('name')
    scope = [
        'https://spreadsheets.google.com/feeds',
        'https://www.googleapis.com/auth/drive'
    ]

    error = None
    url = None
    try:
        credentials = ServiceAccountCredentials.from_json_keyfile_name(google_config, scope)
        gc = gspread.authorize(credentials)
        table = gc.create(table_name + ' ' + company_name)
        table.share('mskuroedov@gmail.com', perm_type='user', role='owner')
        sheet = table.sheet1
        sheet.update_acell('A1', 'БЮДЖЕТ ДВИЖЕНИЯ ДЕНЕЖНЫХ СРЕДСТВ КОМПАНИИ ' + company_name)
        sheet.update_acell('A3', 'Доходы')
        sheet.update_acell('A4', 'Наименование проекта')
        sheet.update_acell('A7', 'Итого Доходов')
        sheet.update_acell('B7', '=SUM(B6:B4)')
        sheet.update_acell('C7', '=SUM(C6:C4)')
        sheet.update_acell('D7', '=SUM(D6:D4)')
        sheet.update_acell('E7', '=SUM(E6:E4)')
        sheet.update_acell('A9', 'Расходы')
        sheet.update_acell('A10', '    Постоянные')
        sheet.update_acell('A11', '    Прочие')
        sheet.update_acell('A13', 'Итого расходы')
        sheet.update_acell('A15', 'Итого Чистая прибыль')
        url = 'https://docs.google.com/spreadsheets/d/%s' % table.id
    except Exception as e:
        error = str(e)

    return JsonResponse({'error': error, 'url': url})
