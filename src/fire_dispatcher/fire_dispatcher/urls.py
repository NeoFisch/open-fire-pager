from django.conf.urls import patterns, include, url
import settings

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'fire_dispatcher.views.home', name='home'),
    # url(r'^fire_dispatcher/', include('fire_dispatcher.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),

    url(r'^fdmanager/', include('fdmanager.urls'), name="fdmanager"),
    url(r'^$', include('fdmanager.urls'), name="default"),
)
