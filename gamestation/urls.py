from django.urls import path
from .views_comprador import *
from .views_distribuidor import *

urlpatterns = [

# HOME

path('', catalogo, name='catalogo'),

# COMPRADOR

path('registro/', registro_comprador, name='registro_comprador'),
path('login/', login_comprador, name='login_comprador'),
path('biblioteca/', biblioteca, name='biblioteca'),
path('comprar/<str:juego_id>/', comprar_juego, name='comprar_juego'),
path('resena/<str:juego_id>/', crear_resena, name='crear_resena'),

# DISTRIBUIDOR

path('registro-distribuidor/', registro_distribuidor, name='registro_distribuidor'),
path('login-distribuidor/', login_distribuidor, name='login_distribuidor'),
path('dashboard/', dashboard_distribuidor, name='dashboard_distribuidor'),
path('mis-juegos/', listar_juegos_distribuidor, name='listar_juegos_distribuidor'),
path('crear-juego/', crear_juego, name='crear_juego'),
path('editar-juego/<str:juego_id>/', editar_juego, name='editar_juego'),
path('eliminar-juego/<str:juego_id>/', eliminar_juego, name='eliminar_juego'),
]