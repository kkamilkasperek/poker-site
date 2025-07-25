from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('register/', views.registerUser, name='register'),
    path('login/', views.loginUser, name='login'),
    path('logout/', views.logoutUser, name='logout'),
    path('rooms/', views.rooms, name='rooms'),
    path('rooms/create/', views.createRoom, name='create_room'),
    path('room/<int:room_id>/', views.joinRoom, name='join_room'),
]