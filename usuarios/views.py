from django.shortcuts import render
from django.views.generic import FormView
from .forms import RegisterForm, LoginForm, ForgotPasswordForm
from deviceio.settings import FIREBASE_CONFIG
import pyrebase
from django.http import HttpResponseRedirect

import json
import urllib.request
import urllib.error

firebase = pyrebase.initialize_app(FIREBASE_CONFIG)
authe = firebase.auth()
db = firebase.database()

# View registro user (note que o controle do form é feito pelo DJANGO, não pelo HTML). O Firebase (tanto o auth como o DB
#são legais, porém eles "alejam" uma série de features que o framework já tem, principalmente na questão de user autenticado

class RegisterView(FormView):
    form_class = RegisterForm
    template_name = 'register.html'

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid(): #função nativa do django que te fala se o form foi preenchido de acordo com o que está no forms.py#
            try:
                #obtendo os dados preenchidos no form
                displayName = form.cleaned_data.get('name')
                email = form.cleaned_data.get('email')
                password = form.cleaned_data.get('password')
                #criação user no firebase AUTH e pegando idToken no response do firebase
                user = authe.create_user_with_email_and_password(email, password)
                
                session_id = user['localId']
                #request.session['uid'] = str(session_id)
                #preparando dados para salvar no firebase DB
                data = {
                    "Name":displayName,
                    "Email":email
                }
                db.child("usuarios").child(session_id).set(data)
                return render(request, 'userhome.html', {'usuario':user['email']})
            except:
                error_message = 'Ops! Este email já está em uso!'
                return render(request, 'register.html', {'form': form, 'error_message': error_message})


#o esquema aqui é similar ao acima, porem a função do auth firebase muda (e só). Note que o template userhome.html não
#precisa nem url (assim vc evita de qquer um entrar ali sem login)
class LoginView(FormView):
    form_class = LoginForm
    template_name = 'login.html'

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            try:
                email = form.cleaned_data.get('email')
                password = form.cleaned_data.get('password')

                user = authe.sign_in_with_email_and_password(email, password)
                session_id = user['idToken']
                request.session['uid'] = str(session_id)
                
                return render(request, 'userhome.html', {'usuario': user['email']})
            except:
                error_message = 'ERROR! Email or password incorrect!'
                return render(request, 'login.html', {'form': form, 'error_message': error_message})


#view funcional, o user clica no botão, ele executa a função e redireciona pra page de login sem contexto ou token de sessão.
def logoutView(request):
    if request.session['uid']:
        del request.session['uid']
        return HttpResponseRedirect('login')
    else:
        return HttpResponseRedirect('login')


def userhome(request):
    return render(request, 'userhome.html')


class ForgotPasswordView(FormView):
    form_class = ForgotPasswordForm
    template_name = 'forgotPassword.html'
    
    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            try:
                email_recover = form.cleaned_data.get('email')
                authe.send_password_reset_email(email_recover)
                message="Password reset. Check your email box"
                return HttpResponseRedirect('login')
            except:
                error_message = 'ERROR! Email not registered!'
                return render(request, 'forgotPassword.html', {'form': form, 'error_message': error_message})


