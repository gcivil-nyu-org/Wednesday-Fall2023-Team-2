from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from . import views

app_name = "users"

urlpatterns = [
    path("login/", views.UserLoginView.as_view(), name="login"),
    path("logout/", views.UserLogoutView.as_view(), name="logout"),
    path("welcome/", views.UserWelcomeView.as_view(), name="welcome"),
    path("register/", views.UserRegisterView.as_view(), name="register"),
    path("profile/<str:username>/", views.UserProfileView.as_view(), name="profile"),
    path(
        "profile-edit/<str:username>/",
        views.UserProfileEditView.as_view(),
        name="profile_edit",
    ),
    path(
        "profile-delete/<str:username>",
        views.UserProfileDeleteView.as_view(),
        name="profile_delete",
    ),
    path("verification/<str:username>", views.UserVerificationView.as_view(), name="verification"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
