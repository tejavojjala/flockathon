from django.conf.urls import url
from travis import views

urlpatterns = [
	url(r'^events$', views.events),
	url(r'^users$', views.getusers),
	url(r'^webhook$',views.travis_incoming_webhook),
]
