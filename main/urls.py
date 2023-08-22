from django.urls import path
from . import views

urlpatterns = [
    path('', views.index),
    path('output/<str:keyword>/', views.output, name='output'),
]