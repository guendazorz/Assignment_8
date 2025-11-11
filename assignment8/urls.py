from django.contrib import admin
from django.urls import path
from network import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('submit/', views.submit_request, name='submit'),
    path('leases/', views.view_leases, name='leases'),
]

