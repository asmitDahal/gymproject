from django.urls import path
from gym_app import views

urlpatterns = [
    path('',views.Home,name="Home"),
    path('signup/',views.signup,name="signup"),
    path('verify_otp/', views.verify_otp, name='verify_otp'),
    path('resend-otp/', views.resend_otp, name='resend_otp'),
    path('login/',views.handlelogin,name="handlelogin"),
    path('logout/',views.handleLogout,name="handleLogout"),
    path('contact/',views.contact,name="contact"),
    path('join/',views.enroll,name="enroll"),
    path('profile/',views.profile,name="profile"),
    path('gallery/',views.gallery,name="gallery"),
    path('attendance/',views.attendance,name="attendance"),
    path('services/', views.service, name='service'),

]
