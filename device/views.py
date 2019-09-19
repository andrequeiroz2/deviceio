from django.shortcuts import render

from django.shortcuts import render
from django.views.generic import FormView
from device.forms import RegisterDeviceForm
import pyrebase
from django.http import HttpResponseRedirect

from django.contrib import messages

from usuarios.views import  authe, db



class RegisterDeviceView(FormView):
    form_class = RegisterDeviceForm
    template_name = 'registerDevice.html'

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            try:
                qrcode      = form.cleaned_data.get('qrcode')
                localDevice = form.cleaned_data.get('local')
                nameDevice  = form.cleaned_data.get('name')
           
                #separa as informacoes do qrcode (mac[12:12:12:12];typeDevice[dht11]) 
                qrcode_split = qrcode.split(';')
                macAddress = qrcode_split[0]
                typeDevice = qrcode_split[1]
                
                idtoken = request.session['uid']
                a = authe.get_account_info(idtoken)
                a = a['users']
                a = a[0]
                a = a['localId']
                
                data = {
                    "macAddress":macAddress,
                    "type":typeDevice,
                    "name":nameDevice,
                    "local":localDevice
                }
                    
                db.child("usuarios").child(a).child("dadosDevice").child(macAddress).set(data, idtoken)
                messages.success(request, 'Seu Device foi Cadastrado com Sucesso!')

                return render(request, 'userhome.html') #, {'usuario': user['email']}
            except:
                error_message = 'Ops! Erro ao Registrar o Device!'
                return render(request, 'registerDevice.html', {'form': form,'error_message': error_message})



def listDevice(request):
    
    idtoken = request.session['uid']
    a = authe.get_account_info(idtoken)
    a = a['users']
    a = a[0]
    a = a['localId']

    lista_Obj_Device = db.child('usuarios').child(a).child('dadosDevice').shallow().get(idtoken).val()
  
    lista_obj = []
    for i in lista_Obj_Device:
        lista_obj.append(i)
    lista_obj.sort(reverse=True)

    local_device = []
    for i in lista_obj:
        db_local_device = db.child('usuarios').child(a).child('dadosDevice').child(i).child('local').get(idtoken).val()
        local_device.append(db_local_device)

    tipo_device = []
    for i in lista_obj:
        db_tipo_device = db.child('usuarios').child(a).child('dadosDevice').child(i).child('type').get(idtoken).val()
        tipo_device.append(db_tipo_device)

    nome_device = []
    for i in lista_obj:
        db_nome_device = db.child('usuarios').child(a).child('dadosDevice').child(i).child('name').get(idtoken).val()
        nome_device.append(db_nome_device)

    lista_Device = zip(lista_obj, local_device, tipo_device, nome_device)
    
    return render(request, 'listDevice.html', {'lista_Device':lista_Device})


def dashboard(request):
    
    elementos = request.GET.get('z')

    idtoken = request.session['uid']
    a = authe.get_account_info(idtoken)
    a = a['users']
    a = a[0]
    a = a['localId']


    macAddress  = db.child('usuarios').child(a).child('dadosDevice').child(elementos).child('macAddress').get(idtoken).val()
    tipoDevice  = db.child('usuarios').child(a).child('dadosDevice').child(elementos).child('type').get(idtoken).val()
    nomeDevice  = db.child('usuarios').child(a).child('dadosDevice').child(elementos).child('name').get(idtoken).val()
    localDevice = db.child('usuarios').child(a).child('dadosDevice').child(elementos).child('local').get(idtoken).val()
    
    topico_composto = ('coffeeiot/', str(tipoDevice), '/', str(macAddress))
    separador = ''
    topico = separador.join(topico_composto)

    return render(request, 'dashboard.html', {'macAddress':macAddress,'tipoDevice':tipoDevice,'nomeDevice':nomeDevice,'localDevice':localDevice,'topico':topico})


