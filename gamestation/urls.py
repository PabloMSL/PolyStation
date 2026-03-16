from django.urls import path
from .views import JuegosApiView, ReseñasApiView, TicketsApiView, FondosApiView
from .views_auth import RegistroAPIView, LoginApiView
from .views_perfil import PerfilImagenAPIview

urlpatterns = [
    path('auth/registro/', RegistroAPIView.as_view(), name='api_registro'),
    path('auth/login/', LoginApiView.as_view(), name='api_login'),

    # Juegos
    path('Juegos/', JuegosApiView.as_view(), name='Juegos'),
    path('Juegos/<str:pk>/', JuegosApiView.as_view(), name="put1"),

    #Reseñas
    path('Reseñas/', ReseñasApiView.as_view(), name='Reseñas'),
    path('Reseñas/<str:pk>/', ReseñasApiView.as_view(), name="put2"),

    path('Fondos/<str:pk>/', FondosApiView.as_view(), name="put3"),

    path('Tickets/', TicketsApiView.as_view(), name='Tickets'),
    path('Tickets/<str:pk>/', TicketsApiView.as_view(), name="put4"),
    
    path("perfil/foto/", PerfilImagenAPIview.as_view(), name="apiperfilfoto")
]