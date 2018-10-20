from django.urls import path
from . import views

app_name = 'api'

urlpatterns = [
    path('sitepingers/',
        views.SitePingerListView.as_view(),
        name='sitepinger_list'
    ),
    path('sitepingers/<int:pk>/',
        views.SitePingerDetailView.as_view(),
        name='sitepinger_detail'
    ),
    path('downtime/',
        views.DowntimeListView.as_view(),
        name='offline_list'
    ),
    path('failures/',
        views.FailureListView.as_view(),
        name='failure_list'
    ),
]
