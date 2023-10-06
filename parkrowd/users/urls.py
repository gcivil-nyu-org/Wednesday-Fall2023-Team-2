from django.urls import path

from . import views

app_name = 'users'

urlpatterns = [
    path('login/', views.UserLoginView.as_view(), name='login'),
    path('profile/<str:username>/', views.UserProfileView.as_view(), name='profile'),
    path('logout/', views.UserLogoutView.as_view(), name='logout')
]