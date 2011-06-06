# Create your views here.
from wptango.tester.models import *
from django.http import HttpResponse
from django.db import connection
from django.shortcuts import render_to_response

def listurls(request):
  r = runnable.objects.all()
  return render_to_response('list.html', {'tests': r})
  
  
def urlreport(request, id):
  r = runnable.objects.get(id=int(id))
  tests = testrun.objects.filter(runnable=r).filter(status=4)
  return render_to_response('url.html', {'tests': tests, 'url': r.name})


def processurls(request):
  for r in runnable.objects.all():
    r.check_schedule()
  for test in testrun.objects.filter(status=1):
    test.submit_to_wpt()
  for test in testrun.objects.filter(status=2):
    test.get_wpt_results()    
  return HttpResponse("OK")
  
"""
def addurl(request):
  url = request.GET["url"]
  t = testrun()
  t.url = url
  t.testid = "temp"
  t.save()
  t.submit_to_wpt()
  return HttpResponse(t.testid)
"""