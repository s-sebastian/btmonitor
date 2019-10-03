import asyncio
import errno
import re
import socket
import time

from bs4 import BeautifulSoup
from hashlib import md5
from pyppeteer import launch
from pyppeteer.errors import BrowserError, TimeoutError
from django.conf import settings
from django.utils import timezone
from django.core.management.base import BaseCommand, CommandError
from api.models import Note, SitePinger

URL = settings.FETCH_URL

def is_online(host='1.1.1.1'):
    try:
        s = socket.create_connection((host, 53), 1)
        s.close()
        return True
    except Exception as e:
        pass

    return False

def hash_value(msg):
    return md5(msg.encode()).hexdigest()

def get_note(error):
    hash = hash_value(error)

    note, created = Note.objects.get_or_create(
        hash=hash, 
        defaults={'hash': hash, 'note_type': error}
    )

    return note

def time_to_sec(t):
    t2 = re.findall(r'(\d+)', t)
    ret = sum(int(n) * m for n, m in zip(reversed(t2), (60, 3600, 86400)))

    return timezone.timedelta(seconds=ret)

async def fetch():
    browser = await launch(
        executablePath='/usr/lib/chromium-browser/libs/chromium-browser',
        headless=True,
        args=['--no-sandbox']
    )
    page = await browser.newPage()
    await page.goto(URL, {'timeout': 10000})
    await page.waitForSelector('[ng-bind="serialNumber"]', options={'timeout': 10000})
    await page.evaluate('''
        const fVer = document.querySelector('[ng-bind="serialNumber"]');
        fVer.innerHTML = fVer.innerHTML.replace(/./g, '*')
    ''')
    await page.screenshot({'path': 'test.png', 'fullPage': True})
    ret = await page.content()
    await browser.close()

    return ret

def parse(html):
    bs = BeautifulSoup(html, 'html.parser')
    status = bs.find(id='conn_status_help').find_next('a').text.strip()
    system_uptime = bs.find(id='system_up_help').find_next('p').text.strip()
    network_uptime = bs.find(id='network_up_help').find_next('p').text.strip()
    down_sync, up_sync = (
        tag.find_next('p').text.strip() for tag in bs.find_all(id='down_sync_help')
    )

    ret = {
        'status': status,
        'system_uptime': time_to_sec(system_uptime),
        'network_uptime': time_to_sec(network_uptime),
        'down_sync': down_sync,
        'up_sync': up_sync
    }

    return ret


class Command(BaseCommand):
    help = 'Pulls data from BTHub and inserts into database'

    def handle(self, *args, **options):
        dt = {}
        error = None
        try:
            start = time.time()
            loop = asyncio.get_event_loop()
            html = loop.run_until_complete(fetch())
            elapsed  = time.time() - start
            dt = parse(html)
            dt['req_time'] = timezone.timedelta(seconds=elapsed)
        except IOError as e:
            if e.errno == errno.ENOSPC:
                error = 'No space left on device'
            else:
                error = e
        except TimeoutError as e:
            dt['status'] = 'Timeout'
            error = e
            raise CommandError(e)
        except BrowserError as e:
            error = 'Failed to connect to local browser'
            raise CommandError(e)
        except Exception as e:
            error = e
            raise CommandError(e)
        finally:
            if error:
                dt['note'] = get_note(str(error))

            dt['online'] = is_online()

            spinger = SitePinger(**dt)
            spinger.save()

        self.stdout.write(self.style.SUCCESS('Data successfully imported'))
