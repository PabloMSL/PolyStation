from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from firebase_admin import auth
import firebase_admin
from principalstation.firebase_config import initialize_firebase

db = initialize_firebase()

class FirebaseAuthentication(BaseAuthentication):
    """
    Lerr el token JWT del encabezado. Lo va a validar con firebase y va a extraer el UID del usuario
    """
    def authenticate(self, request):
       # Extraemos el token
       auth_header = request.META.get('HTTP_AUTHORIZATION') or request.headers.get('Authorization')
       if not auth_header:
           return None #Si no hay token
       
       # El token viene "Bearer <<token>>"

       partes = auth_header.split()

       if len(partes) != 2 or partes[0].lower() != 'bearer':
           return None
       
       token = partes[1]

       try:
            # Le pido a firebase que valide la firma del Token
            decoded_token = auth.verify_id_token(token)
            uid = decoded_token.get('uid')
            email = decoded_token.get('email')
            user_profile = db.collection('perfiles').document(uid).get()
            rol = decoded_token.get('rol')

            if not rol:
                user_doc = db.collection('perfiles').document(uid).get()
                if user_doc.exists:
                    rol = user_doc.to_dict().get('rol', 'comprador')
                else:
                    rol = 'comprador'
            # Usuario
            class FirebaseUser:
               def __init__(self, uid, rol, email):
                   self.uid = uid
                   self.rol = rol
                   self.email = email
                   self.is_authenticated = True
                   self.is_active = True
            
            return(FirebaseUser(uid, rol, email), decoded_token)
       except Exception as e:
           raise AuthenticationFailed(f"Token no es valido o esta expirado: {str(e)}")
       