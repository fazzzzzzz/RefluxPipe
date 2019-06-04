#!/usr/bin/env python
import os
import sys
from multiprocessing.pool import ThreadPool

if __name__ == '__main__':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'RefluxPipe.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    if len(sys.argv) >= 2 and sys.argv[1] == 'runserver' and os.environ.get('RUN_MAIN') == 'true':
        from DnsServer.zoneresolver import dnsinit
        dnsserver_pool = ThreadPool(processes=1)
        dnsserver_pool_list = [dnsserver_pool.apply_async(dnsinit, ())]
    execute_from_command_line(sys.argv)
