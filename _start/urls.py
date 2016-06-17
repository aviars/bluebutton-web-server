from django.conf.urls import include, url
from django.contrib import admin
from apps.accounts.views.oauth2_profile import user_self


admin.autodiscover()

urlpatterns = [
    # Django
    url(r'^admin/', include(admin.site.urls)),

    # HHS OAuth Server
    url(r'^accounts/', include('apps.accounts.urls')),
    url(r'^education/', include('apps.education.urls')),
    url(r'^profile/me$', user_self, name='user_self'),
    url(r'^api/', include('apps.api.urls')),
    # url(r'^api/', include(api_urls)),
    url(r'^fhir/v3/', include('apps.fhir.server.urls')),
    url(r'^bluebutton/fhir/v1/', include('apps.fhir.bluebutton.urls')),
    url(r'^capabilities/', include('apps.capabilities.urls')),
    url(r'^endorsements/', include('apps.dot_ext.endorsementurls')),
    url(r'^o/', include('apps.dot_ext.urls')),
    url(r'^', include('apps.home.urls')),
    # url(r'^fhir/api/v1/',   include('apps.fhir.bluebutton')),
]
