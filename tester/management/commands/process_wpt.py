from django.core.management.base import BaseCommand, CommandError
from tester.models import *

class Command(BaseCommand):
    args = '<None no need>'
    help = 'posts new test requests to wpt, fetches results for previous ones. best to run it every min or smthn'
    def handle(self, *args, **options):
        print "RUNNING"
        for r in runnable.objects.all():
            r.check_schedule(verbose=True)
        for test in testrun.objects.filter(status=1):
            print test
            test.submit_to_wpt()
        for test in testrun.objects.filter(status=2):
            test.get_wpt_results()
        