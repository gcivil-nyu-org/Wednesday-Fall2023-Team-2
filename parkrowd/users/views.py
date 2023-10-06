from django.shortcuts import get_object_or_404, render
from .backends import EmailOrUsernameAuthenticationBackend as EoU

from django.contrib import messages
from django.contrib import auth
from django.contrib.auth.forms import AuthenticationForm

from django.views import View
from .forms import UserLoginForm

from .models import User

from django.shortcuts import redirect

SESSION_COOKIE_EXPIRATION = 86400

# Create your views here.

class UserLoginView(View):
    form_class                      = UserLoginForm
    template_name                   = 'login.html'

    def get(self, request):
        form                        = self.form_class
        return render( request, self.template_name, { 'form': form } )

    def post(self, request):
        print("Logging in")
        form                        = self.form_class(request.POST)    

        username                    = request.POST.get('username')
        password                    = request.POST.get('password')
        remember_me                 = request.POST.get('remember_me')

        user                        = EoU.authenticate(request, username=username, password=password)
        if not user:
            messages.error( request, 'No such user exists' )
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



class UserProfileView(View):
    model                   = User
    template_name           = 'profile.html'

    def get(self, request, username):
        user                = get_object_or_404(User, username=username)
        return render( request, self.template_name )

    def post(self, request, username):
        user                = get_object_or_404(User, username=username)
        return render( request, self.template_name )
    