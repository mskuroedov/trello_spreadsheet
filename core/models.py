from django.contrib.auth.models import User
from django.db import models


class Project(models.Model):
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    title = models.CharField(max_length=100)
    spreadsheet_id = models.CharField(max_length=1000, default='')
    trelloboard_id = models.CharField(max_length=1000, default='')
    spreadsheet_url = models.CharField(max_length=1000, default='')
    trelloboard_url = models.CharField(max_length=1000, default='')

    def __str__(self):
        return self.title
