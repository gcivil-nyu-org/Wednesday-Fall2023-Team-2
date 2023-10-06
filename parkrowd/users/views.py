from django.shortcuts import render
from .backends import EmailorUsernameAuthenticationBackend as EoU

from django.views import View
from .forms import UserLoginForm

# Create your views here.

class UserLoginView(View):
    form_class              = UserLoginForm
    template_name           = 'login.html'

    def get(self, request):
        form                = self.form_class
        return render( request, self.template_name, { 'form': form } )

    def post(self, request):
        print(request.POST.get("username"))
        print(request.POST.get("password"))
        #TO DO : INSERT CLIENT SIDE VALIDATION HERE
        #CURRENT : WILL THROW ERROR IF "Sign In" BUTTON PRESSED
        # messages.error(request, "Email or password incorrect", "danger")