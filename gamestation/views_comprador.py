from django.shortcuts import render, redirect
from django.contrib import messages
from firebase_admin import firestore, auth
from principalstation.firebase_config import initialize_firebase
from functools import wraps
import requests
import os
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt


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


@csrf_exempt  # Vital para que no te rebote el error 403 de CSRF
def registro_comprador(request):
    if request.method == 'POST':
        try:
            # 1. Cargar los datos del JSON
            data = json.loads(request.body)
            
            # 2. Obtener los campos (usa los mismos nombres que mandas en el JSON)
            nombre = data.get('username') # En tu JSON mandas "username", no "nombre"
            email = data.get('email')
            password = data.get('password')

            # 3. Validación básica
            if not email or not password:
                return JsonResponse({"error": "Faltan datos obligatorios"}, status=400)

            # 4. Crear usuario en Firebase
            user = auth.create_user(
                email=email,
                password=password
            )

            # 5. Guardar en Firestore
            db.collection('usuarios').document(user.uid).set({
                'nombre': nombre,
                'email': email,
                'uid': user.uid,
                'rol': 'comprador',
                'fecha_registro': firestore.SERVER_TIMESTAMP
            })

            return JsonResponse({"mensaje": "Usuario registrado", "uid": user.uid}, status=201)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)
    
    return JsonResponse({"error": "Método no permitido"}, status=405)


@csrf_exempt
def login_comprador(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            email = data.get('email')
            password = data.get('password')
            api_key = os.getenv('FIREBASE_WEB_API_KEY')

            url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={api_key}"
            payload = {
                "email": email,
                "password": password,
                "returnSecureToken": True
            }

            response = requests.post(url, json=payload)
            fb_data = response.json()

            if response.status_code == 200:
                # En una API, solemos devolver el token para que el cliente lo guarde
                # Pero si usas sesiones de Django, las mantenemos:
                request.session['uid'] = fb_data['localId']
                request.session['email'] = fb_data['email']
                request.session['rol'] = 'comprador'

                return JsonResponse({
                    "mensaje": "Login exitoso",
                    "token": fb_data.get('idToken'),
                    "uid": fb_data['localId']
                }, status=200)
            else:
                return JsonResponse({"error": "Credenciales inválidas"}, status=401)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)
    return JsonResponse({"error": "Método no permitido"}, status=405)

def catalogo(request):
    # GET no necesita csrf_exempt usualmente si es solo lectura
    juegos = []
    try:
        docs = db.collection('juegos').stream()
        for doc in docs:
            juego = doc.to_dict()
            juego['id'] = doc.id
            juegos.append(juego)
        return JsonResponse(juegos, safe=False, status=200)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

@csrf_exempt
def comprar_juego(request, juego_id):
    if request.method == 'POST':
        uid = request.session.get('uid')
        if not uid:
            return JsonResponse({"error": "No autenticado"}, status=401)
        
        try:
            juego_ref = db.collection('juegos').document(juego_id)
            doc = juego_ref.get()

            if not doc.exists:
                return JsonResponse({"error": "Juego no existe"}, status=404)

            juego = doc.to_dict()
            db.collection('compras').add({
                'usuario_id': uid,
                'juego_id': juego_id,
                'titulo': juego.get('titulo'),
                'precio': juego.get('precio'),
                'fecha_compra': firestore.SERVER_TIMESTAMP
            })

            return JsonResponse({"mensaje": "Compra realizada con éxito"}, status=201)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
    return JsonResponse({"error": "Método no permitido"}, status=405)

def biblioteca(request):
    uid = request.session.get('uid')
    if not uid:
        return JsonResponse({"error": "No autenticado"}, status=401)
        
    juegos = []
    try:
        docs = db.collection('compras').where('usuario_id', '==', uid).stream()
        for doc in docs:
            compra = doc.to_dict()
            compra['id'] = doc.id
            juegos.append(compra)
        return JsonResponse(juegos, safe=False, status=200)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

@csrf_exempt
def crear_resena(request, juego_id):
    if request.method == 'POST':
        uid = request.session.get('uid')
        if not uid:
            return JsonResponse({"error": "No autenticado"}, status=401)

        try:
            data = json.loads(request.body)
            calificacion = data.get('calificacion')
            comentario = data.get('comentario')

            db.collection('resenas').add({
                'usuario_id': uid,
                'juego_id': juego_id,
                'calificacion': int(calificacion),
                'comentario': comentario,
                'fecha': firestore.SERVER_TIMESTAMP
            })

            return JsonResponse({"mensaje": "Reseña publicada"}, status=201)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)
    return JsonResponse({"error": "Método no permitido"}, status=405)