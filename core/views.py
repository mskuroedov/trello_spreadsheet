from __future__ import print_function

import trello
from apiclient.discovery import build
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_POST
from httplib2 import Http
from oauth2client.service_account import ServiceAccountCredentials
from trello import TrelloClient

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
    creds = ServiceAccountCredentials.from_json_keyfile_name(google_config, scope)
    sheets_service = build('sheets', 'v4', http=creds.authorize(Http()))
    drive_service = build('drive', 'v3', http=creds.authorize(Http()))

    error = None
    sheets_url = None
    try:
        sheets_response = sheets_service.spreadsheets().create(
            body={
                "properties": {
                    "title": table_name + ' ' + company_name
                },
                "sheets": [
                    {
                        "data": [
                            {
                                "rowData": [
                                    {
                                        "values": [
                                            {
                                                "userEnteredValue": {
                                                    "stringValue": 'БЮДЖЕТ ДВИЖЕНИЯ ДЕНЕЖНЫХ СРЕДСТВ КОМПАНИИ ' + company_name
                                                },
                                                "userEnteredFormat": {
                                                    "backgroundColor": {
                                                        "red": 0,
                                                        "green": 0,
                                                        "blue": 0.5,
                                                        "alpha": 255
                                                    }
                                                }
                                            }
                                        ]
                                    }
                                ],
                            },
                        ]
                    }
                ]
            }
        ).execute()

        drive_response = drive_service.permissions().create(
            fileId=sheets_response.get('spreadsheetId'),
            body={
                'type': 'user',
                'role': 'owner',
                'emailAddress': 'vladzax95@gmail.com'
            },
            fields='id',
            transferOwnership=True
        ).execute()

        sheets_url = sheets_response.get('spreadsheetUrl')
    except Exception as e:
        error = str(e)

    # trello

    client = TrelloClient(**{
        "api_key": "e041ccfe0c269accb789c65b2314667a",
        "api_secret": "d82c6d6e473bead3e7de85d96af927a8ba621e8a5ce4b7ecaf6ef89276238088",
        "token": "71aebf78a786b366035292ac19f8897b2c97503de3b0165acf74b3e3cbef1f92",
        "token_secret": "your-oauth-token-secret"
    })
    trello_board = client.add_board('Test', permission_level='private')

    return JsonResponse({'error': error, 'sheets_url': sheets_url, 'trello_url': trello_board.url})

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
