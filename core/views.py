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
    table_name = request.POST.get('name')
    scope = [
        'https://spreadsheets.google.com/feeds',
        'https://www.googleapis.com/auth/drive'
    ]

    error = None
    url = None
    try:
        credentials = ServiceAccountCredentials.from_json_keyfile_name(google_config, scope)
        gc = gspread.authorize(credentials)
        sheet = gc.create(table_name)
        sheet.share('vladzax95@gmail.com', perm_type='user', role='owner')
        url = 'https://docs.google.com/spreadsheets/d/%s' % sheet.id
    except Exception as e:
        error = str(e)

    return JsonResponse({'error': error, 'url': url})
