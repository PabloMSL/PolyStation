from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import HttpResponseForbidden
from firebase_admin import firestore, auth
from principalstation.firebase_config import initialize_firebase
from functools import wraps
import requests
import os
from datetime import datetime


db = initialize_firebase()


def login_required_firebase(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        uid = request.session.get('uid')
        if not uid:
            messages.error(request, "❌ Debes iniciar sesión.")
            return redirect('login_distribuidor')
        return view_func(request, *args, **kwargs)
    return wrapper


def registro_distribuidor(request):

    mensaje = None

    if request.method == 'POST':

        nombre = request.POST.get('nombre')
        email = request.POST.get('email')
        empresa = request.POST.get('empresa')
        telefono = request.POST.get('telefono')
        password = request.POST.get('password')

        try:

            user = auth.create_user(
                email=email,
                password=password
            )

            db.collection('distribuidores').document(user.uid).set({

                'nombre': nombre,
                'empresa': empresa,
                'telefono': telefono,
                'email': email,
                'uid': user.uid,
                'rol': 'distribuidor',
                'fecha_registro': firestore.SERVER_TIMESTAMP

            })

            mensaje = "Distribuidor registrado correctamente"

        except Exception as e:

            mensaje = f"Error: {e}"

    return render(request, 'distribuidor/register.html', {'mensaje': mensaje})


def login_distribuidor(request):

    if 'uid' in request.session:
        return redirect('dashboard_distribuidor')

    if request.method == 'POST':

        email = request.POST.get('email')
        password = request.POST.get('password')
        api_key = os.getenv('FIREBASE_WEB_API_KEY')

        url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={api_key}"

        payload = {
            "email": email,
            "password": password,
            "returnSecureToken": True
        }

        response = requests.post(url, json=payload)
        data = response.json()

        if response.status_code == 200:

            request.session['uid'] = data['localId']
            request.session['email'] = data['email']
            request.session['rol'] = 'distribuidor'

            return redirect('dashboard_distribuidor')

        else:

            messages.error(request, "❌ Credenciales incorrectas")

    return render(request, 'distribuidor/login.html')


@login_required_firebase
def dashboard_distribuidor(request):

    uid = request.session.get('uid')
    datos = {}

    try:

        doc = db.collection('distribuidores').document(uid).get()

        if doc.exists:
            datos = doc.to_dict()

    except Exception as e:

        messages.error(request, f"Error {e}")

    return render(request, 'distribuidor/dashboard.html', {'datos': datos})


@login_required_firebase
def listar_juegos_distribuidor(request):

    uid = request.session.get('uid')
    juegos = []

    try:

        docs = db.collection('juegos').where('distribuidor_id', '==', uid).stream()

        for doc in docs:

            juego = doc.to_dict()
            juego['id'] = doc.id
            juegos.append(juego)

    except Exception as e:

        messages.error(request, f"Error {e}")

    return render(request, 'juegos/listar_distribuidor.html', {'juegos': juegos})


@login_required_firebase
def crear_juego(request):

    if request.method == 'POST':

        titulo = request.POST.get('titulo')
        descripcion = request.POST.get('descripcion')
        genero = request.POST.get('genero')
        precio = request.POST.get('precio')
        requisitos = request.POST.get('requisitos')

        uid = request.session.get('uid')

        try:

            db.collection('juegos').add({

                'titulo': titulo,
                'descripcion': descripcion,
                'genero': genero,
                'precio': float(precio),
                'requisitos': requisitos,
                'distribuidor_id': uid,
                'fecha_creacion': firestore.SERVER_TIMESTAMP

            })

            messages.success(request, "🎮 Juego publicado")

            return redirect('listar_juegos_distribuidor')

        except Exception as e:

            messages.error(request, f"Error {e}")

    return render(request, 'juegos/form.html')


@login_required_firebase
def editar_juego(request, juego_id):

    uid = request.session.get('uid')
    juego_ref = db.collection('juegos').document(juego_id)

    try:

        doc = juego_ref.get()

        if not doc.exists:

            messages.error(request, "Juego no existe")

            return redirect('listar_juegos_distribuidor')

        juego = doc.to_dict()

        if juego.get('distribuidor_id') != uid:

            return HttpResponseForbidden()

        if request.method == 'POST':

            titulo = request.POST.get('titulo')
            descripcion = request.POST.get('descripcion')
            genero = request.POST.get('genero')
            precio = request.POST.get('precio')
            requisitos = request.POST.get('requisitos')

            juego_ref.update({

                'titulo': titulo,
                'descripcion': descripcion,
                'genero': genero,
                'precio': float(precio),
                'requisitos': requisitos,
                'fecha_actualizacion': firestore.SERVER_TIMESTAMP

            })

            messages.success(request, "Juego actualizado")

            return redirect('listar_juegos_distribuidor')

    except Exception as e:

        messages.error(request, f"Error {e}")

    return render(request, 'juegos/editar.html', {'juego': juego, 'id': juego_id})


@login_required_firebase
def eliminar_juego(request, juego_id):

    uid = request.session.get('uid')

    try:

        juego_ref = db.collection('juegos').document(juego_id)
        doc = juego_ref.get()

        if not doc.exists:

            messages.error(request, "Juego no existe")

            return redirect('listar_juegos_distribuidor')

        if doc.to_dict().get('distribuidor_id') != uid:

            return HttpResponseForbidden()

        juego_ref.delete()

        messages.success(request, "Juego eliminado")

    except Exception as e:

        messages.error(request, f"Error {e}")

    return redirect('listar_juegos_distribuidor')