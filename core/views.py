from __future__ import print_function

import sys

import calendar
import datetime
import json
import locale
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_POST
from trello import TrelloClient

from core.models import UserSettings
from core.spreadsheets_helpers import Table, Sheet, sheets_service, drive_service
from trello_spreadsheets_django.consts import settings_file, trello_config

if sys.platform == 'win32':
    locale.setlocale(locale.LC_ALL, 'rus_rus')
else:
    locale.setlocale(locale.LC_ALL, 'ru_RU.UTF-8')


def index(request):
    return render(request, 'index.html')


@require_POST
def create_table(request):
    table_name = request.POST.get('table')
    company_name = request.POST.get('name')

    with open(settings_file, 'r') as file_obj:
        settings = json.load(file_obj)

    current_month = datetime.date.today().month
    months = []
    for month in range(current_month, current_month + 3):
        months.append(calendar.month_name[month])

    error = None
    try:
        table = Table('Бюджет движения денежных средств компании "%s"' % company_name)
        sheet = Sheet('БДДС')
        table.addSheet(sheet)
        sheet.addRow( #1
            titles=['Доходы'],
            default_color='#6d9eeb'
        ).addRow( #2
            titles=['Возможные доходы'],
            default_color='#c9daf8'
        ).addRow( #3
            titles=['Наименование проекта', 'Единицы измерения'] + months,
            default_color='#c9daf8'
        ).addRow( #4
            titles=[''],
        ).addRow( #5
            titles=['Итого возможных доходов', 'руб.', '=SUM(C4)', '=SUM(D4)', '=SUM(E4)'],
            types=['stringValue', 'stringValue', 'formulaValue', 'formulaValue', 'formulaValue'],
            default_color='#c9daf8'
        ).addRow( #6
            titles=[''],
        ).addRow( #7
            titles=['Подтвержденные доходы'],
            default_color='#ffff00'
        ).addRow( #8
            titles=['Наименование проекта', 'Единицы измерения'] + months,
            default_color='#ffff00'
        ).addRow( #9
            titles=[''],
        ).addRow( #10
            titles=['Итого доходов', 'руб.', '=SUM(C9)','=SUM(D9)','=SUM(E9)'],
            types=['stringValue', 'stringValue', 'formulaValue', 'formulaValue', 'formulaValue'],
            default_color='#93c47d'
        ).addRow( #11
            titles=[''],
        ).addRow( #12
            titles=['Расходы'],
            default_color='#f4cccc'
        ).addRow( #13
            titles=['  Постоянные'],
            default_color='#f4cccc'
        ).addRow( #14
            titles=[''],
        ).addRow( #15
            titles=['Итого расходов', 'руб.', '=SUM(C14)', '=SUM(D14)', '=SUM(E14)'],
            types=['stringValue', 'stringValue', 'formulaValue', 'formulaValue', 'formulaValue'],
            default_color='#93c47d'
        ).addRow( #16
            titles=[''],
        ).addRow( #17
            titles=['Итого чистая прибыль', 'руб.', '=SUM(C10;-C15)', '=SUM(D10;-D15)', '=SUM(E10;-E15)'],
            types=['stringValue', 'stringValue', 'formulaValue', 'formulaValue', 'formulaValue'],
            default_color='#93c47d'
        )

        sheets_response = sheets_service.spreadsheets().create(body=table.body).execute()
        tbl = Table(id=sheets_response.get('spreadsheetId'))

        # sheets_service.spreadsheets().batchUpdate(
        #     spreadsheetId=sheets_response.get('spreadsheetId'),
        #     body={
        #         "requests": [
        #             {
        #                 "insertDimension": {
        #                     "range": {
        #                         "sheetId": 0,
        #                         "dimension": "ROWS",
        #                         "startIndex": 1,
        #                         "endIndex": 3
        #                     },
        #                     "inheritFromBefore": False
        #                 }
        #             },
        #         ],
        #     }
        # ).execute()
        # sheets_service.spreadsheets().values().batchClear(
        #     spreadsheetId=sheets_response.get('spreadsheetId'),
        #     body={
        #         "ranges": [
        #             string
        #         ]
        #     }
        # ).execute()
        # sheets_service.spreadsheets().values().batchUpdate(
        #     spreadsheetId=sheets_response.get('spreadsheetId'),
        #     body={
        #         "valueInputOption": "RAW",
        #         "data": []
        #     }
        # ).execute()

        drive_response = drive_service.permissions().create(
            fileId=sheets_response.get('spreadsheetId'),
            body={
                'type': 'user',
                'role': 'owner',
                'emailAddress': settings.get('owner_email')
            },
            fields='id',
            transferOwnership=True
        ).execute()
    except Exception as e:
        error = str(e)

    # trello

    with open(trello_config, 'r') as file_obj:
        trello_credentials = json.load(file_obj)
        client = TrelloClient(**trello_credentials)
    trello_board = client.add_board(company_name, permission_level='private')
    for trello_list in trello_board.all_lists():
        trello_list.close()

    chek_list = trello_board.add_list('Планирование')
    chek_list = trello_board.add_list('Проекты в работе')
    chek_list = trello_board.add_list('Завершенные проекты')
    # здесь сетап на 1 этап
    # имя проекта
    trello_card = chek_list.add_card('Project 1')
    # чек-лист 1 этапа
    trello_card.add_checklist(
        'step_name',
        [
            'Подготовить техноэкономическое обоснование', 'Оценка по проекту',
            'Предоставить коммерческое предложение заказчику',
            'Формирование ТЗ по требованиям заказчика', 'Планирование бюджета проекта',
            'Переключить статус проекта',
        ]
    )

    us = UserSettings.objects.create(
        user_id=1,
        spreadsheet_id=sheets_response.get('spreadsheetId'),
        spreadsheet_url=sheets_response.get('spreadsheetUrl'),
        trelloboard_id=trello_board.id,
        trelloboard_url=trello_board.url
    )

    return JsonResponse({
        'error': error,
        'sheets_url': us.spreadsheet_url,
        'trello_url': us.trelloboard_url
    })

# @require_POST
# def create_table(request):
#     table_name = request.POST.get('table')
#     company_name = request.POST.get('name')
#     scope = [
#         'https://spreadsheets.google.com/feeds',
#         'https://www.googleapis.com/auth/drive'
#     ]
#
#     error = None
#     url = None
#     try:
#         credentials = ServiceAccountCredentials.from_json_keyfile_name(google_config, scope)
#         gc = gspread.authorize(credentials)
#         table = gc.create(table_name + ' ' + company_name)
#         table.share('vladzax95@gmail.com', perm_type='user', role='owner')
#         # table.share('mskuroedov@gmail.com', perm_type='user', role='owner')
#         sheet = table.sheet1
#         sheet.update_acell('A1', 'БЮДЖЕТ ДВИЖЕНИЯ ДЕНЕЖНЫХ СРЕДСТВ КОМПАНИИ ' + company_name)
#         sheet.update_acell('A3', 'Доходы')
#         sheet.update_acell('A4', 'Наименование проекта')
#         sheet.update_acell('A7', 'Итого Доходов')
#         sheet.update_acell('B7', '=SUM(B6:B4)')
#         sheet.update_acell('C7', '=SUM(C6:C4)')
#         sheet.update_acell('D7', '=SUM(D6:D4)')
#         sheet.update_acell('E7', '=SUM(E6:E4)')
#         sheet.update_acell('A9', 'Расходы')
#         sheet.update_acell('A10', '    Постоянные')
#         sheet.update_acell('A11', '    Прочие')
#         sheet.update_acell('A13', 'Итого расходы')
#         sheet.update_acell('A15', 'Итого Чистая прибыль')
#         url = 'https://docs.google.com/spreadsheets/d/%s' % table.id
#     except Exception as e:
#         error = str(e)
#
#     return JsonResponse({'error': error, 'url': url})
