from django.shortcuts import render, redirect
from django.contrib import messages
from firebase_admin import firestore, auth
from principalstation.firebase_config import initialize_firebase
from functools import wraps
import requests
import os


db = initialize_firebase()


def login_required_firebase(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        uid = request.session.get('uid')
        if not uid:
            messages.error(request, "Debes iniciar sesión")
            return redirect('login_comprador')
        return view_func(request, *args, **kwargs)
    return wrapper


def registro_comprador(request):

    mensaje = None

    if request.method == 'POST':

        nombre = request.POST.get('nombre')
        email = request.POST.get('email')
        password = request.POST.get('password')

        try:

            user = auth.create_user(
                email=email,
                password=password
            )

            db.collection('usuarios').document(user.uid).set({

                'nombre': nombre,
                'email': email,
                'uid': user.uid,
                'rol': 'comprador',
                'fecha_registro': firestore.SERVER_TIMESTAMP

            })

            mensaje = "Usuario registrado"

        except Exception as e:

            mensaje = f"Error {e}"

    return render(request, 'usuarios/register.html', {'mensaje': mensaje})


def login_comprador(request):

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
            request.session['rol'] = 'comprador'

            return redirect('catalogo')

        else:

            messages.error(request, "Error de autenticación")

    return render(request, 'usuarios/login.html')


@login_required_firebase
def catalogo(request):

    juegos = []

    try:

        docs = db.collection('juegos').stream()

        for doc in docs:

            juego = doc.to_dict()
            juego['id'] = doc.id
            juegos.append(juego)

    except Exception as e:

        messages.error(request, f"Error {e}")

    return render(request, 'catalogo/listar.html', {'juegos': juegos})


@login_required_firebase
def comprar_juego(request, juego_id):

    uid = request.session.get('uid')

    try:

        juego_ref = db.collection('juegos').document(juego_id)
        doc = juego_ref.get()

        if not doc.exists:

            messages.error(request, "Juego no existe")

            return redirect('catalogo')

        juego = doc.to_dict()

        db.collection('compras').add({

            'usuario_id': uid,
            'juego_id': juego_id,
            'titulo': juego.get('titulo'),
            'precio': juego.get('precio'),
            'fecha_compra': firestore.SERVER_TIMESTAMP

        })

        messages.success(request, "Compra realizada")

    except Exception as e:

        messages.error(request, f"Error {e}")

    return redirect('biblioteca')


@login_required_firebase
def biblioteca(request):

    uid = request.session.get('uid')
    juegos = []

    try:

        docs = db.collection('compras').where('usuario_id', '==', uid).stream()

        for doc in docs:

            compra = doc.to_dict()
            compra['id'] = doc.id
            juegos.append(compra)

    except Exception as e:

        messages.error(request, f"Error {e}")

    return render(request, 'biblioteca/listar.html', {'juegos': juegos})


@login_required_firebase
def crear_resena(request, juego_id):

    uid = request.session.get('uid')

    if request.method == 'POST':

        calificacion = request.POST.get('calificacion')
        comentario = request.POST.get('comentario')

        try:

            db.collection('resenas').add({

                'usuario_id': uid,
                'juego_id': juego_id,
                'calificacion': int(calificacion),
                'comentario': comentario,
                'fecha': firestore.SERVER_TIMESTAMP

            })

            messages.success(request, "Reseña publicada")

        except Exception as e:

            messages.error(request, f"Error {e}")

    return redirect('catalogo')