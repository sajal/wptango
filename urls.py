from django.conf.urls.defaults import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    url(r'^$', 'wptango.tester.views.listurls', name='home'),
    url(r'^urlreport/(.*)/', 'wptango.tester.views.urlreport', name='urlreport'),
    url(r'^process/', 'wptango.tester.views.processurls', name='process'),
#    url(r'^addurl/', 'wptango.tester.views.addurl', name='addurl'),
    # url(r'^wptmon/', include('wptmon.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
)
