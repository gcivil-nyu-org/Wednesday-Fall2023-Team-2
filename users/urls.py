from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from . import views

app_name = 'users'

urlpatterns = [
    path('register/', views.UserRegisterView.as_view(), name='register'),
    path('login/', views.UserLoginView.as_view(), name='login'),
    path('profile/<str:username>/', views.UserProfileView.as_view(), name='profile'),
    path('profile-edit/<str:username>/', views.UserProfileEditView.as_view(), name='profile_edit'),
    path('profile-delete/', views.UserProfileDeleteView.as_view(), name='profile_delete'),
    path('logout/', views.UserLogoutView.as_view(), name='logout'),
    path('welcome/', views.UserWelcomeView.as_view(), name='welcome')
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)