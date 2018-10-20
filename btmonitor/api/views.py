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
    #queryset = SitePinger.objects.filter(~Q(status='Connected') & Q(online=False)).order_by('-created')
    #queryset = SitePinger.objects.filter(note__isnull=False)
    #queryset = SitePinger.objects.select_related('note').filter(note__isnull=False)
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

    def get(self, request, format=None):
        results = []
        total = timezone.timedelta()
        tz = timezone.get_current_timezone()
        queryset = SitePinger.objects.filter(
            created__month=timezone.datetime.today().month
        ).streaks()
        #[{f'start: {start[0]}', f'end: {end[0]}', f'duration: {end[0] - start[0]}'}
        #    for start, end in SitePinger.objects.streaks() if start[1] is False]
        for i, entry in enumerate(queryset, 1):
            start, end = entry
            duration = end[0] - start[0]
            total += duration
            results.append({
                'id': i, 
                'start': start[0].astimezone(tz),
                'end': end[0].astimezone(tz),
                'duration': duration,
            })
        results = sorted(results, key=lambda k: k['id'], reverse=True)
        offline = {'total': total, 'results': results}
        return Response(offline)
