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
    model                   = User
    template_name           = 'profile.html'

    def get(self, request, username):
        user                = get_object_or_404(User, username=username)
        return render( request, self.template_name, {'user': user})

    def post(self, request, username):
        user                = get_object_or_404(User, username=username)
        return render( request, self.template_name )
    
class UserProfileEditView(View):
    model = User
    template_name = 'profile_edit.html'
    username = None

    def get(self, request, username):
        self.username = username
        user = get_object_or_404(User, username=username)
        return render( request, self.template_name, {'user': user})

    def post(self, request, username):
        exists = False
       
        new_username = request.POST.get('input-username')
        new_email = request.POST.get('input-email')
        new_description = request.POST.get('input-description')
        user = get_object_or_404(User, username=username)
        if User.objects.filter(username = new_username).exists() and user.username != new_username:
            exists = True
            return render( request, self.template_name, {'user': user, 'new_username':new_username, 'exists': exists})
        user.username = new_username
        user.email = new_email
        user.description = new_description

        user.save()

        return redirect('/profile/' + user.username)
    