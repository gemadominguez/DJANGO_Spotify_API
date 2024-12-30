from django.urls import path
from .views import view_usuarios, view_usuario_concreto, view_favoritos_usuario

urlpatterns = [
    path('usuarios/', view_usuarios.as_view(), name='usuarios-api'),
    path('usuarios/<str:nombre>/', view_usuario_concreto.as_view(), name='usuario-en-detalle'),
    path('usuarios/<str:nombre>/favoritos/', view_favoritos_usuario.as_view(), name='favoritos-de-spotify-usuario'),

]