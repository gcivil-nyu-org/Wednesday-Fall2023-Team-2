"""user views
"""
from django.views import View
from django.urls import reverse
from django.contrib import auth
from django.contrib import messages
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, render, redirect

from .models import User, Post
from .forms import UserRegisterForm, UserLoginForm
from .backends import EmailOrUsernameAuthenticationBackend

SESSION_COOKIE_EXPIRATION = 86400
emailOrUsernameAuthenticationBackend = EmailOrUsernameAuthenticationBackend()


class UserRegisterView(View):
    """user register view"""

    form_class = UserRegisterForm
    template_name = "register.html"

    def get(self, request: HttpRequest) -> HttpResponse:
        """return user register view page

        Args:
            request (HttpRequest): http request object

        Returns:
            HttpResponse: rendered user register view response
        """
        context = {"form": self.form_class()}
        return render(request, self.template_name, context)

    def post(self, request: HttpRequest) -> HttpResponse:
        """handle user registion post req

        Args:
            request (HttpRequest): http request object

        Returns:
            HttpResponse: redirect or register view with error hints
        """
        form = self.form_class(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.email = request.POST.get("email")
            user.set_password(request.POST.get("password1"))
            user.save()
            return redirect(reverse("users:welcome"))
        return render(request, self.template_name, {"form": form})


class UserLoginView(View):
    """user login view"""

    form_class = UserLoginForm
    template_name = "login.html"

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

        username = request.POST.get("username")
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

            return redirect(
                reverse("users:profile", kwargs={"username": user.username})
            )

        return render(request, self.template_name, {"form": form})


class UserLogoutView(View):
    """user logout view"""

    def post(self, request: HttpRequest) -> HttpResponse:
        """handle user logout post req

        Args:
            request (HttpRequest): http request object

        Returns:
            HttpResponse: redirect user to login page
        """
        auth.logout(request)
        return redirect(reverse("users:login"))


class UserWelcomeView(View):
    """user welcome view"""

    template_name = "welcome.html"

    def get(self, request: HttpRequest) -> HttpResponse:
        """return user welcome view

        Args:
            request (HttpRequest): http request object

        Returns:
            HttpResponse: rendered user welcome view
        """
        return render(request, self.template_name)


class UserProfileView(View):
    """user profile view"""

    model = User
    template_name = "profile.html"

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

        # * conditionally render the delete button
        # * only if the user is logged-in and viewing his/her own profile
        is_user_owner_of_profile = request.user.username == username

        context = {
            "user": user,
            "user_posts": user_posts,
            "is_user_owner_of_profile": is_user_owner_of_profile,
        }

        return render(request, self.template_name, context)


class UserProfileEditView(View):
    """user profile edit view"""

    model = User
    template_name = "profile_edit.html"

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

        new_username = request.POST.get("input-username")
        new_email = request.POST.get("input-email")
        new_avatar = request.FILES["input-avatar"]
        new_description = request.POST.get("input-description")
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

        return redirect(reverse("users:profile", kwargs={"username": user.username}))


class UserProfileDeleteView(View):
    """user profile deleted view

    renders after successful deletion of account
    using the "Delete Account" button
    """

    template_name = "profile_delete.html"

    def get(self, request: HttpRequest) -> HttpResponse:
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
                return redirect("users:profile-delete")

            except User.DoesNotExist:
                messages.error(request, "User does not exist")
                return render(request, self.template_name)

            except Exception:
                messages.error(request, "An error has occurred.  Please try again.")
                return render(request, self.template_name)

        return render(request, self.template_name)
