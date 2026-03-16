import requests
import time
import getpass
from google import genai
from google.genai import types

# 1. Funcion de login
def login_usuario():
    print("--- Login De Usuario ---")
    email = input("Email: ")
    password = getpass.getpass("Contraseña: ")
    url_login = "http://127.0.1:8000/apis/login/"
    
    
    try:
        response = requests.post(url_login, json={"email": email, "password": password})
        if response.status_code == 200:
            print("Usuario loggeado exitosamente")
            return response.json().get("token")
        print(f"Error: {response.json().get('error')}")
    except Exception as e:
        print(f"Error de conexion")
    return None

# Herramineta
def consultar_mis_juegos(token_firebase):
    """
    Consulta los juegos del usuario autenticado usando el token de firebase
    """
    
    print("EL SISTEMA ESTA CONSULTANDO TUS JUEGOS...")
    url = "http://127.0.1:8000/apis/mis-juegos/"
    headers = {"Authorization": f"Bearer {token_firebase}"}
    
    try:
        response = requests.get(url, headers=headers)
        return response.json()
    except Exception as e:
        return {"error": str(e)}

# 3. Configuracion de la IA

API_KEY = 'AIzaSyBkYHDtY1SdDVOGzzbgq79fL40cZHHPJkQ'
client = genai.Client(api_key=API_KEY)

modelo_id = 'gemini-2.5-flash'

#4. Flujo de la logica

token = login_usuario()
if token:
    print("IA: Hola, veo que has iniciado sesion. ¿Quieres que te muestre tus juegos?")
    
    while True:
        user_input = input("\nTu: ")
        if user_input.lower() in ['salir', 'exit', 'chao', 'bye']:break
        
        
        prompt = (
            f"Contexto de seguridad: El token es {token}"
            f"Usuario pregunta: {user_input}"
            f"Usa 'Consultar_mis_juegos' si es necesario."
        )
        
        try: 
            # Llamar al modelo para que el maneje las herramientas
            response = client.models.generate_content(
                model=modelo_id,
                contents=prompt,
                config=types.GenerateContentConfig(
                    tools=[consultar_mis_juegos]
                )
            )
            print(f"IA: {response.text}")
        except Exception as e:
            # Manejo de errores
            error_str = str(e)
            if "429" in error_str:
                print ("IA: Agotaste tu cuota de consultas. Espera un momento antes de volver a intentar.")
                time.sleep(20)
            elif "404" in error_str:
                print("IA: El recurso que intentas acceder no existe. Verifica tu solicitud.")
            else:
                print(f" Ups, ocurrió un error inesperado: {e}")