from django.urls import path
from checkurl import views

urlpatterns = [
    path('', views.checkurl_main, name='checkurl_main'),
    path('api/endpoint/', views.url_check_endpoint, name='url_check_endpoint'),
]