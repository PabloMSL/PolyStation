from rest_framework.views import APIView
from rest_framework.response import Response
from .authentication import FirebaseAuthentication # Ajusta la ruta según tu proyecto
from .permissions import IsAdministrador, IsVendedor

class VistaParaAdmnistradores(APIView):
    # Esto le dice a DRF que use Firebase para esta vista
    authentication_classes = [FirebaseAuthentication]
    # Esto restringe el acceso solo a los que tengan rol 'cliente'
    permission_classes = [IsAdministrador]

    def get(self, request):
        return Response({"mensaje": f"Hola cliente {request.user.email}"})

class VistaParaVendedores(APIView):
    authentication_classes = [FirebaseAuthentication]
    permission_classes = [IsVendedor]

    def post(self, request):
        return Response({"mensaje": "Producto creado por el vendedor"})