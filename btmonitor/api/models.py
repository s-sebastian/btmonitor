from decimal import Decimal
from django.db import models
from django.utils import timezone

# Create your models here.


class Note(models.Model):
    hash = models.CharField(max_length=32, unique=True)
    note_type = models.CharField(max_length=50)


    def __str__(self):
        return f'{self.hash}, {self.note_type}'


class SitePinger(models.Model):
    status = models.CharField(max_length=20, default='Unknown')
    system_uptime = models.DurationField(default=timezone.timedelta)
    network_uptime = models.DurationField(default=timezone.timedelta)
    down_sync = models.CharField(max_length=20, default='Not Available')
    up_sync = models.CharField(max_length=20, default='Not Available')
    req_time = models.DurationField(default=timezone.timedelta)
    created = models.DateTimeField(db_index=True, default=timezone.now)
    online = models.BooleanField()
    note = models.ForeignKey(Note, on_delete=models.SET_DEFAULT, default=None, null=True)

    def __str__(self):
        return f'{self.status}, {self.created}'
