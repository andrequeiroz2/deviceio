from django import forms


class RegisterDeviceForm(forms.Form):
    qrcode  = forms.CharField(max_length=150, required=True)
    local   = forms.CharField(max_length=150, required=True)
    name    = forms.CharField(max_length=150, required=True)