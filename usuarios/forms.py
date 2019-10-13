from django import forms


class RegisterForm(forms.Form):
    name     = forms.CharField(max_length=150, required=True)
    email    = forms.EmailField(max_length=100, required=True)
    password = forms.CharField(widget=forms.PasswordInput, required=True)


class LoginForm(forms.Form):
    email = forms.EmailField(max_length=100, required=True)
    password = forms.CharField(widget=forms.PasswordInput, required=True)

class ForgotPasswordForm(forms.Form):
    email = forms.EmailField(max_length=100, required=True)