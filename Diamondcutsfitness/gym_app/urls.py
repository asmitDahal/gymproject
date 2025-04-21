
from django.urls import path
from gym_app import views

urlpatterns = [
    path('',views.Home,name="Home"),
]
