from django.urls import path
from . import views 

urlpatterns = [
    path('', views.Home, name= 'home'),
    path('about', views.About, name= 'about'),
    path('contact', views.Contact, name='contact'),
    path('kitchen', views.Kitchen, name= 'kitchen'),
    path('living_room', views.Living_room, name= 'living_room'),
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('verify-otp/', views.verify_otp_view, name='verify_otp'),
    path('resend-otp/', views.resend_otp_view, name='resend_otp'),
]