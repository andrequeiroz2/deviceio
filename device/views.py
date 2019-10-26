from django.shortcuts import render

from django.shortcuts import render
from django.views.generic import FormView
from device.forms import RegisterDeviceForm
import pyrebase
from django.http import HttpResponseRedirect

from django.contrib import messages

from usuarios.views import  authe, db

NAME_PROJECT = 'deviceio'

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
                typeDevice = qrcode_split[0]
                macAddress = qrcode_split[1]
                
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
                messages.success(request, 'Your device has been successfully registered')

                return render(request, 'userhome.html') #, {'usuario': user['email']}
            except:
                error_message = 'ERROR! Unable to register your device!'
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

    key_device = []
    for i in lista_obj:
        db_key_device = db.child('usuarios').child(a).child('dadosDevice').child(i).child('macAddress').get(idtoken).val()
        key_device.append(db_key_device)

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

    lista_Device = zip(lista_obj, key_device, local_device, tipo_device, nome_device)
    
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
    
    topico = topic_composer(tipoDevice,macAddress)

    return render(request, 'dashboard.html', {'macAddress':macAddress,'tipoDevice':tipoDevice,'nomeDevice':nomeDevice,'localDevice':localDevice,'topico':topico})


def topic_composer(tipoDevice, macAddress):

    topic_sub = ['temperature','humidity','status','dateFailure']
    topic     = []
    topics    = []

    device = str(tipoDevice)
    mac    = str(macAddress)

    if device == 'dht11' or 'dht22':

        for i in range(len(topic_sub)):
            topic = topic_sub[i]
            topic_composition = (NAME_PROJECT, '/', device, '/', mac, '/', topic)
            topic_sub[i]
            agglutinate = ''
            topics.append(agglutinate.join(topic_composition))
        return topics
        
