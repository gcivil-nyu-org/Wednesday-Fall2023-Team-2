"""user views
"""
from django.views import View
from django.contrib import auth
from django.contrib import messages
from django.shortcuts import get_object_or_404, render, redirect
from .backends import EmailOrUsernameAuthenticationBackend as EoU

from .models import User
from .forms import UserRegisterForm, UserLoginForm

SESSION_COOKIE_EXPIRATION = 86400

class UserRegisterView(View):
    """user register view
    """
    form_class = UserRegisterForm
    template_name = 'register.html'

    def get(self, request):
        """get for user register view
        """
        form = self.form_class()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        """post to handle user registration
        """
        form = self.form_class(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.email = request.POST.get('email')
            user.set_password(request.POST.get('password1'))
            user.save()
            #messages.success(request, 'Success')
            return redirect("/welcome")
        else:
            return render(request, self.template_name, {'form': form})



class UserLoginView(View):
    form_class                      = UserLoginForm
    template_name                   = 'login.html'

    def get(self, request):
        form                        = self.form_class
        return render( request, self.template_name, { 'form': form } )

    def post(self, request):
        form                        = self.form_class(request.POST)    

        username                    = request.POST.get('username')
        password                    = request.POST.get('password')
        remember_me                 = request.POST.get('remember_me')

        user                        = EoU.authenticate(request, username=username, password=password)
        if not user:
            messages.error( request, 'No such user exists with those credentials exist' )
        else:
            auth.login(request, user)
            messages.success( request, 'You have successfully logged in!' )

            if remember_me: request.session.set_expiry(SESSION_COOKIE_EXPIRATION)
            else: request.session.set_expiry(0)

            return redirect('/profile/' + user.username)
        
        return render( request, self.template_name, { 'form': form } )



class UserLogoutView(View):
    template_name           = 'logout.html'
    
    def get(self, request):
        return redirect('/login')

    def post(self, request):
        auth.logout(request)
        return redirect('/login')
    

class UserWelcomeView(View):
    template_name           = 'welcome.html'
    
    def get(self, request):
        return render(request, self.template_name )



class UserProfileView(View):
    """user profile view
    """
    model                        = User
    template_name                = 'profile.html'

    def get(self, request, username):
        user                     = get_object_or_404(User, username=username)

        #For Conditionally rendering "Delete Account" button
        #only if user is viewing their own profile
        is_user_owner_of_profile = request.user.username == username

        payload = {
            'user': user, 
            'is_user_owner_of_profile': is_user_owner_of_profile
        }

        return render( request, self.template_name, payload )

    def post(self, request, username):
        if "delete_profile" in request.POST:
            username             = request.user.username

            try:
                user = User.objects.get(username=username)
                user.delete()
                return redirect('/profile-delete')            

            except User.DoesNotExist:
                messages.error(request, "User does not exist")    
                return render(request, self.template_name)

            except Exception as e: 
                messages.error(request, "An error has occurred.  Please try again.")
                return render(request, self.template_name)

        return render( request, self.template_name )



class UserProfileDeleteView(View):
    """user profile deleted view

        renders after successful deletion of account
        using the "Delete Account" button
    """
    template_name           = 'profile_delete.html'

    def get(self, request):
        return render( request, self.template_name )
