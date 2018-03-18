from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('login/', views.login, name='login'),
    path('get_command/<str:command>/', views.get_command, name='get_command'),
    path('get_command_ajax/<str:command>/', views.get_command_ajax, name='get_command_ajax'),
    path('new/', views.new, name='new'),
    path('new/<str:extra>/', views.new, name='new'),
    path('notifycheck/', views.notifychecker, name='notifychecker'),
    path('listmem/', views.listmem, name='listmem'),
    path('listdb/', views.listdb, name='listdb'),
    path('logout/', views.logout, name='logout'),
]
