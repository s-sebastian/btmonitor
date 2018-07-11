from rest_framework import pagination


class SitePingerPagination(pagination.LimitOffsetPagination):
    default_limit = 60
    max_limit = 1440
