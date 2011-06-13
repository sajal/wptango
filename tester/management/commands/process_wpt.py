from django.core.management.base import BaseCommand, CommandError
from tester.models import *

class Command(BaseCommand):
    args = '<None no need>'
    help = 'posts new test requests to wpt, fetches results for previous ones. best to run it every min or smthn'
    def handle(self, *args, **options):
        print "RUNNING"