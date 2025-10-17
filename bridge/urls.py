from django.urls import path

from bridge import views

app_name = 'bridge'

urlpatterns = [
    path('', views.index, name='index'),
]