import random

from django.test import Client, TestCase
from django.db.transaction import atomic
from django.utils import timezone
from .models import SitePinger

# Create your tests here.

def gen_data():
    n = 100
    until = timezone.now()
    with atomic():
        for timestamp in (
            until - timezone.timedelta(minutes=i * 30)
            for i in range(n, 0, -1)):
                SitePinger.objects.create(
                    created=timestamp,
                    online=(random.random() > .65)
                )

class SitePingerTestCase(TestCase):
    def setUp(self):
        gen_data()
        self.client = Client()

    def test_downtime(self):
        fmt = '%Y/%m'
        date = timezone.now().strftime(fmt)
        response = self.client.get(f'/api/downtime/{date}/')
        self.assertEqual(response.status_code, 200)
        resp_date = timezone.datetime.strptime(
            response.json()['date'],
            '%Y-%m-%dT%H:%M:%S'
        )
        self.assertEqual(resp_date.strftime(fmt), date)

    def test_invalid_date(self):
        response = self.client.get('/api/downtime/2018/13/')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['detail'], 'Invalid date.')
