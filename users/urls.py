from django.urls import path

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
        name="profile-edit",
    ),
    path(
        "profile-delete/<str:username>",
        views.UserProfileDeleteView.as_view(),
        name="profile-delete",
    ),
    path(
        "password-reset",
        views.UserPasswordResetView.as_view(),
        name="password-reset",
    ),
    path(
        "password-reset-email-sent",
        views.UserPasswordResetEmailSentView.as_view(),
        name="password-reset-email-sent",
    ),
    path(
        "password-reset-confirm/<uidb64>/<token>",
        views.UserPasswordResetConfirmView.as_view(),
        name="password-reset-confirm",
    ),
    path(
        "password-reset-success",
        views.UserPasswordResetSuccessView.as_view(),
        name="password-reset-success",
    ),
    path(
        "verification/<str:username>",
        views.UserVerificationView.as_view(),
        name="verification",
    ),
    path(
        "verification-cancel/<int:id>",
        views.VerificationCancelView.as_view(),
        name="verification-cancel",
    ),
]
