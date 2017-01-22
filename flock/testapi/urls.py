from django.conf.urls import url
from testapi import views
from django.views.decorators.csrf import csrf_exempt

urlpatterns = [
	url(r'^testapi$', views.testapi),
	url(r'^processapi$', csrf_exempt(views.process_api_request)),
]
