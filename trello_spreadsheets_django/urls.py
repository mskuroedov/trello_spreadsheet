from django.contrib import admin
from django.urls import path

from core.views import *

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', index),
    path('table/create', create_table),
]
