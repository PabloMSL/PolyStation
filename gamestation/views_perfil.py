import cloudinary
import cloudinary.uploader
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated
from .authentication import FirebaseAuthentication
from principalstation.firebase_config import initialize_firebase

db = initialize_firebase()

class PerfilImagenAPIview(APIView):
    authentication_classes = [FirebaseAuthentication]
    permission_classes = [IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)
    
    def post(self,request):
        file_to_upload = request.FILES.get('imagen')
        
        
        if not file_to_upload:
            return Response({"error": "No se envio ninguna imagen"}, status=status.HTTP_400_BAD_REQUEST)
        
        try: 
            uid = request.user.uid
            
            # 1. Subir a cloudinary
            # 'folder' nos va a organizar las fotos
            
            upload_result = cloudinary.uploader.upload(
                file_to_upload, folder=f"adso/perfiles/{uid}/",
                public_id="foto_principal",
                overwrite=True
            )
            
            # 2. Obtener la url optimizada
            # Cloudinary nos da una url segura HTTPS
            url_imagen = upload_result.get('secure_url')
            
            # 3. Guardar la url en firestore
            db.collection('perfiles').document(uid).update({
                'foto_url': url_imagen
            })
            
            return Response({"Mensaje": "Foto de perfil actualizada", "url": url_imagen}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"Error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            