from django.utils import timezone
from rest_framework import generics
from rest_framework.renderers import JSONRenderer
from api.models import Note, SitePinger
from api.serializers import SitePingerSerializer
from api.pagination import SitePingerPagination


# Create your views here.

threshold = timezone.now() - timezone.timedelta(hours=1)


class SitePingerListView(generics.ListAPIView):
    """
    Returns a list of all SitePingers
    """
    queryset = SitePinger.objects.all().order_by('-created')
    #queryset = SitePinger.objects.filter(created__gt=threshold)
    #queryset = SitePinger.objects.filter(note__isnull=False)
    #queryset = SitePinger.objects.select_related('note').filter(note__isnull=False)
    #renderer_classes = [JSONRenderer]
    serializer_class = SitePingerSerializer
    pagination_class = SitePingerPagination


class SitePingerDetailView(generics.RetrieveAPIView):
    """
    Return a single SitePinger
    """
    queryset = SitePinger.objects.all()
    serializer_class = SitePingerSerializer
