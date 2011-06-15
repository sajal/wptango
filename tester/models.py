from django.db import models
import urllib
import json
# Create your models here.
from BeautifulSoup import BeautifulStoneSoup
from email.utils import parsedate_tz, mktime_tz
from datetime import datetime
from django.conf import settings

STATUS_CHOICES = (
(1, 'PENDING'),
(2, 'SUBMITED'),
(3, 'ERROR'),
(4, 'COMPLETE'),
)


class runnable(models.Model):
    name = models.CharField(max_length=50, help_text="A name, this will be shown in reports")
    url = models.CharField(max_length=250, help_text="URL to hit, this will be ignored for scripted tests, but pls fill it here.")
    location = models.CharField(max_length=50, default="Dulles_IE8", help_text="(unsupported currently)Which WPT location to use? see http://www.webpagetest.org/getLocations.php")
    run_every = models.IntegerField(default=60, help_text="How often should this run, in minutes - Dont get greedy or sajal's unlimited api key may get banned!")
    
    
    
    
    script = models.TextField(null=True, blank=True, help_text="WPT script - advanced usage")
    blocks = models.TextField(null=True, blank=True, help_text="URL blocks, space delimeted - advanced usage")

    def check_schedule(self, verbose = False):
        tests = testrun.objects.filter(runnable=self)
        if verbose:
            print tests
        if len(tests) == 0:
            #no tests run yet, lets run one
            self.add_task(verbose = verbose)
        else:
            #Get timestamp of latest applied test
            t = tests[0]
            #print (datetime.now() - t.submitted).total_seconds()
            if (datetime.now() - t.submitted).total_seconds() > self.run_every * 60:
                self.add_task(verbose = verbose)
    
    def add_task(self,verbose = False):
        """
        Adds a new testrun object
        """
        t = testrun()
        t.url = self.url
        t.runnable = self
        t.script = self.script
        t.save()
        print "Adding %s" %(t)
        t.submit_to_wpt()

class testrun(models.Model):
    testid = models.CharField(max_length=50, null=True, blank=True)
    status = models.IntegerField(default = 1, choices=STATUS_CHOICES, db_index=True)
    runnable = models.ForeignKey('runnable')
    first_ttfb = models.IntegerField(null=True, blank=True)
    first_load = models.IntegerField(null=True, blank=True)
    first_render = models.IntegerField(null=True, blank=True)
    repeat_ttfb = models.IntegerField(null=True, blank=True)
    repeat_load = models.IntegerField(null=True, blank=True)
    repeat_render = models.IntegerField(null=True, blank=True)
    url = models.CharField(max_length=250)
    submitted = models.DateTimeField(auto_now_add=True, db_index=True)
    completed = models.DateTimeField(null=True, blank=True)
    script = models.TextField(null=True, blank=True)
    blocks = models.TextField(null=True, blank=True, help_text="URL blocks, space delimeted - advanced usage")
    location = models.CharField(max_length=50, default="Dulles_IE8", help_text="(unsupported currently)Which WPT location to use? see http://www.webpagetest.org/getLocations.php")

    class Meta:
        ordering = ["-submitted"]
    
    def submit_to_wpt(self):
        if self.status != 1:
            raise Exception("Status is %s" %(self.status) )
            #print self.url
        testurl = "http://www.webpagetest.org/runtest.php?url=%s&block=ga.js&f=json&private=1&location=%s" %(self.url, self.location)
        #TODO: implement callback rather than frequent poling
        print testurl
        try:
            testurl += '&k=' + settings.WPTAPI
        except:
            pass
        resp = json.loads(urllib.urlopen(testurl).read())
        self.testid = resp['data']['testId']
        self.status = 2
        self.save()
    
    def get_wpt_results(self):
        if self.status != 2:
            raise Exception("Status is %s" %(self.status) )
        print "Getting result for : %s" %(self.testid)
        print self.testid
        try:
            resulturl = "http://www.webpagetest.org/xmlResult/%s/" %(self.testid)
            print resulturl
            resp = urllib.urlopen(resulturl).read()
            soup = BeautifulStoneSoup(resp)
            status = soup.response.statustext.contents[0]
            print "Status: %s" %(status)
            if status == 'Ok':
                    #Todo: need to check median not average.. has more data
                self.first_ttfb = soup.response.data.median.firstview.ttfb.contents[0]
                self.first_load = soup.response.data.median.firstview.loadtime.contents[0]
                self.first_render = soup.response.data.median.firstview.render.contents[0]
                self.repeat_ttfb = soup.response.data.median.repeatview.ttfb.contents[0]
                self.repeat_load = soup.response.data.median.repeatview.loadtime.contents[0]
                self.repeat_render = soup.response.data.median.repeatview.render.contents[0]
                self.completed = datetime.fromtimestamp(mktime_tz(parsedate_tz(soup.response.data.completed.contents[0])))
                self.status = 4
                self.save()
    
        except:
            #raise
            print "errr"