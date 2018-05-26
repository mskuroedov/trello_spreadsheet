import os

from trello_spreadsheets_django.settings import BASE_DIR

google_config = os.path.join(BASE_DIR, 'creds', 'trellosreadsheets.json')
client_secret = os.path.join(BASE_DIR, 'creds', 'client_secret.json')
credentials = os.path.join(BASE_DIR, 'creds', 'credentials.json')
