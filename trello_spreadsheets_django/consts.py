import os

from trello_spreadsheets_django.settings import BASE_DIR

google_config = os.path.join(BASE_DIR, 'creds', 'trellosreadsheets.json')
trello_config = os.path.join(BASE_DIR, 'creds', 'trello.json')
settings_file = os.path.join(BASE_DIR, 'creds', 'settings.json')
