from django.conf.urls import url

from .views import default_view

urlpatterns = [
    url(r'^$', default_view, name='data_collector'),
]
