from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'ecsite.views.home', name='home'),
    # url(r'^ecsite/', include('ecsite.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
    (r'(?P<item_id>\d+)/$', 'itempage.views.item_page_display'),
    (r'^itemsearch', 'itempage.views.item_search'),
    (r'^cart', 'itempage.views.do_cart'),
)
