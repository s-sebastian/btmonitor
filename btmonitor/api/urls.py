from django.urls import path
from . import views

app_name = 'api'

urlpatterns = [
    path('sitepingers/',
        views.SitePingerListView.as_view(),
        name='sitepinger_list'
    ),
    path('sitepingers/<pk>/',
        views.SitePingerDetailView.as_view(),
        name='sitepinger_detail'
    ),
]
