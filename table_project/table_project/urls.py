"""table_project URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from rate import views
from map.views import HotelMap,EditHotelMap

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^qunar_room$', views.qunar_room),
    url(r'^hotelrate$', views.hotelRate),

    url(r'^$', views.index),
    url(r'^getHotelRate$', views.getHotelRate),
    # url(r'^hotelsearch', views.HotelSearch.as_view()),
    # url(r'^getHotelSearch', views.HotelSearch.as_view()),
    url(r'^getHotelMap', HotelMap.as_view()),
    url(r'^EditHotelMap', EditHotelMap.as_view()),


]
