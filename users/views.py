"""user views
"""
from django.utils import timezone
from django.views import View
from django.contrib import auth
from django.contrib import messages
from django.http import HttpRequest, HttpResponse
from django.core.exceptions import ValidationError
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.contrib.auth.views import INTERNAL_RESET_SESSION_TOKEN

from .models import User, Post, UserVerification
from .backends import EmailOrUsernameAuthenticationBackend
from .forms import (
    UserLoginForm,
    UserRegisterForm,
    UserVerificationForm,
    UserPasswordResetForm,
    UserPasswordResetConfirmForm,
    EditPostForm,
)

from better_profanity import profanity

profanity.load_censor_words()

UserModel = auth.get_user_model()
# * Expiration is 1 week
SESSION_COOKIE_EXPIRATION = 604800
emailOrUsernameAuthenticationBackend = EmailOrUsernameAuthenticationBackend()


class UserRegisterView(View):
    """user register view"""

    form_class = UserRegisterForm
    template_name = "users/register.html"

    def get(self, request: HttpRequest) -> HttpResponse:
        """return user register view page

        Args:
            request (HttpRequest): http request object

        Returns:
            HttpResponse: rendered user register view response
        """
        context = {"form": self.form_class(None)}
        return render(request, self.template_name, context)

    def post(self, request: HttpRequest) -> HttpResponse:
        """handle user registion post req

        Args:
            request (HttpRequest): http request object

        Returns:
            HttpResponse: redirect or register view with error hints
        """
        form = self.form_class(request.POST.copy())
        form.data["username"] = profanity.censor(form.data["username"])
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.email = request.POST.get("email")
            user.set_password(request.POST.get("password1"))
            user.save()
            return redirect("users:welcome")
        return render(request, self.template_name, {"form": form})


class UserLoginView(View):
    """user login view"""

    form_class = UserLoginForm
    template_name = "users/login.html"

    def get(self, request: HttpRequest) -> HttpResponse:
        """return user login page

        Args:
            request (HttpRequest): http request object

        Returns:
            HttpResponse: rendered user login page response
        """
        context = {"form": self.form_class()}
        return render(request, self.template_name, context)

    def post(self, request: HttpRequest) -> HttpResponse:
        """handle user login post req

        Args:
            request (HttpRequest): http request object

        Returns:
            HttpResponse: redirect or login view with error hints
        """
        form = self.form_class(request.POST)

        username = profanity.censor(request.POST.get("username"))
        password = request.POST.get("password")
        remember_me = request.POST.get("remember_me")

        user = emailOrUsernameAuthenticationBackend.authenticate(
            request, username=username, password=password
        )
        if not user:
            messages.error(
                request, "The credentials you provided do not match any user."
            )
        else:
            auth.login(request, user)
            messages.success(request, "You have successfully logged in!")

            if remember_me:
                request.session.set_expiry(SESSION_COOKIE_EXPIRATION)

            return redirect("users:profile", username=user.username)

        return render(request, self.template_name, {"form": form})


class UserLogoutView(
    LoginRequiredMixin,
    View,
):
    """user logout view"""

    def post(self, request: HttpRequest) -> HttpResponse:
        """handle user logout post req

        Args:
            request (HttpRequest): http request object

        Returns:
            HttpResponse: redirect user to login page
        """
        auth.logout(request)
        return redirect("users:login")


class UserWelcomeView(View):
    """user welcome view"""

    template_name = "users/welcome.html"

    def get(self, request: HttpRequest) -> HttpResponse:
        """return user welcome view

        Args:
            request (HttpRequest): http request object

        Returns:
            HttpResponse: rendered user welcome view
        """
        return render(request, self.template_name)


class UserPasswordResetView(View):
    """user login view"""

    form_class = UserPasswordResetForm
    template_name = "users/password_reset.html"
    extra_email_context = {"site_name": "Parkrowd"}

    def get(self, request: HttpRequest) -> HttpResponse:
        """return user password reset page

        Args:
            request (HttpRequest): http request object

        Returns:
            HttpResponse: rendered user password reset page response
        """
        context = {"form": self.form_class()}
        return render(request, self.template_name, context)

    def post(self, request: HttpRequest) -> HttpResponse:
        """handle user password reset req

        Args:
            request (HttpRequest): http request object

        Returns:
            HttpResponse: redirect to login or return password reset page with errors
        """
        form = self.form_class(request.POST)
        if not form.is_valid():
            return render(request, self.template_name, {"form": form})

        # * check to make sure the email corresponds to a user
        users = list(form.get_users(request.POST.get("email")))
        if len(users) == 0:
            messages.error(
                request,
                "This email does not match any of our records, please check for any typos",
            )
            return render(request, self.template_name, {"form": form})
        opts = {
            "request": request,
            "use_https": self.request.is_secure(),
            "extra_email_context": self.extra_email_context,
            "email_template_name": form.email_template_name,
            "subject_template_name": form.subject_template_name,
        }
        form.save(**opts)
        return redirect("users:password-reset-email-sent")


class UserPasswordResetEmailSentView(View):
    """user password reset email sent view"""

    template_name = "users/password_reset_email_sent.html"

    def get(self, request: HttpRequest) -> HttpResponse:
        """return user password reset email sent page

        Args:
            request (HttpRequest): http request object

        Returns:
            HttpResponse: rendered user password reset email sent page response
        """
        return render(request, self.template_name)


class UserPasswordResetConfirmView(View):
    """user password reset confirm view"""

    form_class = UserPasswordResetConfirmForm
    token_generator = PasswordResetTokenGenerator()
    template_name = "users/password_reset_confirm.html"
    reset_url_token = "reset-password"

    def get_user(self, uidb64):
        try:
            # urlsafe_base64_decode() decodes to bytestring
            uid = urlsafe_base64_decode(uidb64).decode()
            user = UserModel._default_manager.get(pk=uid)
        except (
            TypeError,
            ValueError,
            OverflowError,
            UserModel.DoesNotExist,
            ValidationError,
        ):
            user = None
        return user

    def get(self, request: HttpRequest, uidb64, token) -> HttpResponse:
        """return user password reset confirmation page

        Args:
            request (HttpRequest): http request object

        Returns:
            HttpResponse: rendered user password reset confirmation page
        """
        user = self.get_user(uidb64)
        context = {"uidb64": uidb64, "token": token, "form": self.form_class(user)}
        if not user:
            messages.error(
                request,
                "User not found. Please contact site admin if you believe this is an error.",
            )
            return render(request, self.template_name, context)

        if token != self.reset_url_token:
            if self.token_generator.check_token(user, token):
                self.request.session[INTERNAL_RESET_SESSION_TOKEN] = token
                redirect_url = request.path.replace(token, self.reset_url_token)
                return redirect(redirect_url)
            messages.error(
                request, "Your reset passsword URL is invalid or has expired"
            )
            return render(request, self.template_name, context)

        return render(request, self.template_name, context)

    def post(self, request: HttpRequest, uidb64, token) -> HttpResponse:
        user = self.get_user(uidb64)
        form = self.form_class(user, request.POST)
        context = {"uidb64": uidb64, "token": token, "form": form}
        if not user:
            messages.error(
                request,
                "User not found. Please contact site admin if you believe this is an error.",
            )
            return render(request, self.template_name, context)

        if self.token_generator.check_token(
            user, request.session.get(INTERNAL_RESET_SESSION_TOKEN)
        ):
            if not form.is_valid():
                return render(request, self.template_name, context)
            try:
                form.clean_new_password2()
            except ValidationError as validationError:
                messages.error(request, validationError)
                return render(request, self.template_name, context)
            form.save()
            return redirect("users:password-reset-success")

        messages.error(request, "Your reset password URL is invalid or has expired")
        return render(request, self.template_name, context)


class UserPasswordResetSuccessView(View):
    """user password reset success view"""

    template_name = "users/password_reset_success.html"

    def get(self, request: HttpRequest) -> HttpResponse:
        """return user password reset success page

        Args:
            request (HttpRequest): http request object

        Returns:
            HttpResponse: rendered user password reset success page response
        """
        return render(request, self.template_name)


class UserProfileView(View):
    """user profile view"""

    model = User
    template_name = "users/profile.html"

    def get(self, request: HttpRequest, username: str) -> HttpResponse:
        """return user profile view

        Args:
            request (HttpRequest): http request object
            username (str): username string

        Returns:
            HttpResponse: rendered user profile view
        """
        user = get_object_or_404(User, username=username)
        user_posts = Post.objects.filter(author=user)
        user_verification = UserVerification.objects.filter(username=user).last()

        # * conditionally render the delete button
        # * only if the user is logged-in and viewing his/her own profile
        is_user_owner_of_profile = request.user.username == username

        user.username_human = user.username.capitalize()
        user.description = (
            user.description
            if user.description
            else "This user was lazy and left no description here."
        )
        context = {
            "user": user,
            "user_posts": user_posts,
            "is_user_owner_of_profile": is_user_owner_of_profile,
            "user_verification": user_verification,
        }

        return render(request, self.template_name, context)


class UserProfileEditView(
    LoginRequiredMixin,
    View,
):
    """user profile edit view"""

    model = User
    template_name = "users/profile_edit.html"

    def get(self, request: HttpRequest, username: str) -> HttpResponse:
        """return user profile edit page

        Args:
            request (HttpRequest): http request object
            username (str): username string

        Returns:
            HttpResponse: rendered user profile edit page
        """
        context = {"user": get_object_or_404(User, username=username)}
        return render(request, self.template_name, context)

    def post(self, request: HttpRequest, username: str) -> HttpResponse:
        """handle user profile edit post req

        Args:
            request (HttpRequest): http request object
            username (str): username string

        Returns:
            HttpResponse: redirect back to profile page
        """

        new_username = profanity.censor(request.POST.get("input-username"))
        new_email = request.POST.get("input-email")
        new_avatar = request.FILES.get("input-avatar", request.user.avatar)
        new_description = profanity.censor(request.POST.get("input-description"))
        user = get_object_or_404(User, username=username)
        # * if username is already taken
        if (
            User.objects.filter(username=new_username).exists()
            and user.username != new_username
        ):
            return render(
                request,
                self.template_name,
                {"user": user, "new_username": new_username, "exists": True},
            )
        user.username = new_username
        user.email = new_email
        user.avatar = new_avatar
        user.description = new_description
        user.save()

        return redirect("users:profile", username=user.username)


class UserProfileDeleteView(LoginRequiredMixin, View):
    """user profile deleted view

    renders after successful deletion of account
    using the "Delete Account" button
    """

    # TODO: get method and tempalte is no longer in use
    template_name = "users/profile_delete.html"

    def get(self, request: HttpRequest, username: str) -> HttpResponse:
        return render(request, self.template_name)

    def post(self, request: HttpRequest, username: str) -> HttpResponse:
        """handle user profile delete post req

        Args:
            request (HttpRequest): http request object
            username (str): username string

        Returns:
            HttpResponse: rendered user profile view with error messages or redirect to profile-delete page
        """
        if "delete_profile" in request.POST:
            username = request.user.username

            try:
                user = User.objects.get(username=username)
                user.delete()
                auth.logout(request)
                return redirect("users:register")

            except User.DoesNotExist:
                messages.error(request, "User does not exist")
                return render(request, self.template_name)

            except Exception:
                messages.error(request, "An error has occurred.  Please try again.")
                return render(request, self.template_name)

        return render(request, self.template_name)


class UserVerificationView(View):
    """user verification request view"""

    form_class = UserVerificationForm
    template_name = "users/verification.html"

    def get(self, request: HttpRequest, username: str) -> HttpResponse:
        """return user profile edit page

        Args:
            request (HttpRequest): http request object
            username (str): username string

        Returns:
            HttpResponse: rendered user profile edit page
        """
        user = get_object_or_404(User, username=username)
        user_verification = UserVerification.objects.filter(username=user)
        non_active_status = ["verified", "cancelled"]
        active_verification = UserVerification.objects.filter(username=user).exclude(
            status__in=non_active_status
        )

        context = {
            "user": user,
            "user_verification": user_verification,
            "active_verification": active_verification,
        }
        return render(request, self.template_name, context)

    def post(self, request: HttpRequest, username: str) -> HttpResponse:
        """handle user verification post request
        Args:
            request (HttpRequest): http request object
            username (str): username string

        Returns:
            HttpResponse: rendered user profile view with error messages or redirect to profile-delete page
        """

        form = self.form_class(request.POST, request.FILES)
        if form.is_valid():
            verification = form.save(commit=False)
            verification.username = get_object_or_404(User, username=username)
            verification.business_name = request.POST.get("business_name")
            verification.business_type = form.cleaned_data["business_type"]
            verification.business_address = request.POST.get("business_address")
            verification.uploaded_file = form.cleaned_data.get("uploaded_file")
            verification.save()
            return redirect("users:profile", username=username)
        else:
            messages.error(
                request, "Please resubmit the application with all necessary fields."
            )
            return redirect("users:profile", username=username)


class EditPost(View):
    """edit post view"""

    model = Post
    form_class = EditPostForm
    template_name = "users/edit_post.html"

    def get(self, request: HttpRequest, username: str, post_id: int) -> HttpResponse:
        """return edit post page

        Args:
            request (HttpRequest): http request object
            username (str): username string
            post_id (str): post id/primary key

        Returns:
            HttpResponse: rendered edit post page
        """
        post = get_object_or_404(Post, id=post_id)
        context = {"post": post}

        if request.user == post.author:
            return render(request, self.template_name, context)
        else:
            return HttpResponse(status=403)

    def post(self, request: HttpRequest, username: str, post_id: str) -> HttpResponse:
        """handle edit post

        Args:
            request (HttpRequest): http request object
            username (str): username string
            post_id (str): post id/primary key

        Returns:
            HttpResponse: redirect back to profile page
        """
        new_title = profanity.censor(request.POST.get("title"))
        new_post = profanity.censor(request.POST.get("post"))
        post = get_object_or_404(Post, id=post_id)

        if not new_post.strip():
            return redirect("users:edit_post", username=username, post_id=post_id)

        post.title = new_title
        post.post = new_post
        post.created_at = timezone.now()
        post.save()
        # currently only editing posts from profile page
        # if "users" in (request.META.get("HTTP_REFERER")):
        #   return redirect("users:profile", username=username)
        # else:
        #   return redirect("map:parking")
        return redirect("users:profile", username=username)


class VerificationCancelView(View):
    """verification cancel view"""

    def post(self, request: HttpRequest, id: int) -> HttpResponse:
        """handle verification cancel post req

        Args:
            request (HttpRequest): http request object

        Returns:
            HttpResponse: redirect user to verification page
        """
        verification = get_object_or_404(UserVerification, id=id)
        username = verification.username.username
        verification.status = "cancelled"
        verification.save()
        return redirect("users:verification", username=username)
