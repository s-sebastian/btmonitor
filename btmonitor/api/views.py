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
            created__month=date.month
        ).streaks()
        for i, entry in enumerate(queryset, 1):
            start, end = entry
            duration = end[0] - start[0]
            total += duration
            results.append({
                'start': start[0].astimezone(tz),
                'end': end[0].astimezone(tz),
                'duration': duration,
            })
        results = sorted(results, key=lambda k: k['start'], reverse=True)
        offline = {'date': date.strftime('%b-%Y'), 'total': total, 'results': results}
        return offline

    def get(self, request, year=None, month=None, format=None):
        month = (timezone.now() - timezone.timedelta(days=3*365/12)).month
        months = SitePinger.objects.filter(created__month__gt=month) \
            .annotate(month=TruncMonth('created')) \
            .values_list('month', flat=True).distinct().order_by('-month')
        return Response([self.get_data(m) for m in months])
