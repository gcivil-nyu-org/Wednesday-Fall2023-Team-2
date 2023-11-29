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
        "profile-edit/",
        views.UserProfileEditView.as_view(),
        name="profile-edit",
    ),
    path(
        "profile-delete/",
        views.UserProfileDeleteView.as_view(),
        name="profile-delete",
    ),
    path(
        "password-reset/",
        views.UserPasswordResetView.as_view(),
        name="password-reset",
    ),
    path(
        "password-reset-email-sent/",
        views.UserPasswordResetEmailSentView.as_view(),
        name="password-reset-email-sent",
    ),
    path(
        "password-reset-confirm/<uidb64>/<token>/",
        views.UserPasswordResetConfirmView.as_view(),
        name="password-reset-confirm",
    ),
    path(
        "password-reset-success/",
        views.UserPasswordResetSuccessView.as_view(),
        name="password-reset-success",
    ),
    path(
        "verification/",
        views.UserVerificationView.as_view(),
        name="verification",
    ),
    path(
        "edit_post/<int:post_id>/",
        views.EditPost.as_view(),
        name="edit-post",
    ),
    path(
        "verification-cancel/<int:id>/",
        views.VerificationCancelView.as_view(),
        name="verification-cancel",
    ),
]
