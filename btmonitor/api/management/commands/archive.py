from django.core.management.base import BaseCommand, CommandError
from django.db import connection
from django.db.models import Count, Min, Max
from django.utils import timezone
from api.models import SitePinger


class Command(BaseCommand):
    help = 'Deletes old records on master server only'

    def add_arguments(self, parser):
        parser.add_argument('--hours', type=int, default=24,
            help='Deletes records older than so many hours, 0 deletes all (default: %(default)s).')
        parser.add_argument('--dry-run', action='store_true',
            help='Do not actually deletes the records (default: %(default)s).')

    def handle(self, *args, **options):
        try:
            kwargs = {
                'created__lt': timezone.now() - timezone.timedelta(hours=options['hours'])
            }
            if options['dry_run']:
                qs = SitePinger.objects.filter(**kwargs).aggregate(
                    Min('created'), Max('created'), count=Count('*')
                )
                msg = self.style.WARNING('DRY-RUN: ') + f'{qs["count"]} record(s) will be deleted'
                if qs['count'] != 0:
                    msg += f' [{qs["created__min"]} <--> {qs["created__max"]}]'
            else:
                with connection.cursor() as cur:
                    cur.execute('SET @@session.sql_log_bin = 0')
                    msg = self.style.SUCCESS('OK: ') + f'{SitePinger.objects.filter(**kwargs).delete()}'
                    cur.execute('SET @@session.sql_log_bin = 1')
        except Exception as e:
            raise CommandError(e)

        self.stdout.write(msg)
