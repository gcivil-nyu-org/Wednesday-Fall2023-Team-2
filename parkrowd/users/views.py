from django.shortcuts import redirect, render
from .backends import EmailorUsernameAuthenticationBackend as EoU

from django.views import View
from .forms import UserRegisterForm, UserLoginForm
from django.contrib import messages

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

class UserRegisterView(View):
    form_class              = UserRegisterForm
    template_name           = 'register.html'

    def get(self, request):
        form = self.form_class()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            print("worked")
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.email = request.POST.get('email')
            user.set_password(request.POST.get('password'))
            user.save()
            messages.success(request, 'Success')
            return redirect("/login")
        else:
            print("no work")
            return render(request, self.template_name, {'form': form})