from django.db.models.functions import TruncMonth
from django.utils import timezone
from rest_framework import generics, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import SitePinger
from .serializers import SitePingerSerializer
from .pagination import SitePingerPagination


class SitePingerListView(generics.ListAPIView):
    """
    Returns a list of all SitePingers
    """
    queryset = SitePinger.objects.all()
    serializer_class = SitePingerSerializer
    pagination_class = SitePingerPagination


class SitePingerDetailView(generics.RetrieveAPIView):
    """
    Returns a single SitePinger
    """
    queryset = SitePinger.objects.all()
    serializer_class = SitePingerSerializer


class FailureListView(generics.ListAPIView):
    """
    Returns a list of all SitePingers with no internet connection
    """
    queryset = SitePinger.objects.filter(online=False)
    serializer_class = SitePingerSerializer
    pagination_class = SitePingerPagination


class DowntimeListView(APIView):
    """
    Returns a list of all downtimes
    """
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    @staticmethod
    def get_data(date):
        results = []
        total = timezone.timedelta()
        tz = timezone.get_current_timezone()
        queryset = SitePinger.objects.filter(
            created__month=date.month,
            created__year=date.year,
        )
        if not queryset.exists():
            return {'detail': 'No data available.'}
        for i, entry in enumerate(queryset.streaks(), 1):
            start, end = entry
            duration = end[0] - start[0]
            total += duration
            results.append({
                'start': start[0].astimezone(tz),
                'end': end[0].astimezone(tz),
                'duration': duration,
            })
        results = sorted(results, key=lambda k: k['start'], reverse=True)
        offline = {'date': date, 'total': total, 'results': results}
        return offline

    def get(self, request, year=None, month=None, format=None):
        if not year or not month:
            today = timezone.now()
            year = today.year
            month = today.month
        try:
            date = timezone.datetime(year=year, month=month, day=1)
        except ValueError as e:
            return Response({'detail': 'Invalid date.'}, status=400)
        return Response(self.get_data(date))


# Notes

# SitePingerListView() - a few queryset exmaples
'''
queryset = SitePinger.objects.filter(~Q(status='Connected') & Q(online=False)).order_by('-created')
queryset = SitePinger.objects.filter(note__isnull=False)
queryset = SitePinger.objects.select_related('note').filter(note__isnull=False)
'''

# get_data() - list comprehension to get the results
'''
[{f'start: {start[0]}', f'end: {end[0]}', f'duration: {end[0] - start[0]}'}
    for start, end in SitePinger.objects.streaks() if start[1] is False]
'''

# get() - Group by month using itertools.groupby
'''
>>> from api.models import SitePinger
>>> from api.views import DowntimeListView
>>> import itertools
>>> obj = DowntimeListView()
>>> res = obj.get('req')
>>> res.status_code
200
>>> for group, igroup in itertools.groupby(data[0]['results'], lambda i: i['start'].strftime('%Y-%m')):
...     print(group)
...     for entry in igroup:
...         print(entry['start'], entry['end'])
... 
2018-11
2018-11-08 04:15:08.109883+00:00 2018-11-08 04:19:15.740350+00:00
2018-11-02 21:16:10.363187+00:00 2018-11-02 21:17:10.005428+00:00
2018-11-02 03:07:16.088278+00:00 2018-11-02 03:08:15.894782+00:00
'''
