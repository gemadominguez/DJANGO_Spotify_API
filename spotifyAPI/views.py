import os
import requests
import base64
import time
from dotenv import load_dotenv
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Tabla_Usuario, Tabla_Favoritos_Usuario
from .serializers import Serializar_Tabla_Usuario, Serializar_Tabla_Favoritos_Usuario

# <--- TOKEN SPOTIFY y ACTUALIZACIÓN TOKEN --->
load_dotenv()
CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")

access_token = None
token_expiration_time = None

def obtener_token_spotify():
    global access_token, token_expiration_time
    
    if access_token and time.time() < token_expiration_time:
        return access_token

    url = "https://accounts.spotify.com/api/token"
    
    credentials = f"{CLIENT_ID}:{CLIENT_SECRET}"
    credentials_base64 = base64.b64encode(credentials.encode()).decode()

    headers = {
        "Authorization": f"Basic {credentials_base64}",
        "Content-Type": "application/x-www-form-urlencoded"
    }

    data = {
        "grant_type": "client_credentials"
    }
    response = requests.post(url, headers=headers, data=data)

    if response.status_code == 200:
        data = response.json()
        access_token = data.get("access_token")
        
        print(f"Token obtenido: {access_token}")
        
        expires_in = data.get("expires_in", 3600) 
        token_expiration_time = time.time() + expires_in  
        
        return access_token
    else:
        print(f"Error al obtener el token de Spotify: {response.status_code} - {response.text}")
        raise Exception("No se pudo obtener el token de Spotify")



# <----- FUNCIONES EXTERNAS PARA HACER PETICIONES A SPOTIFY ----->
def obtener_id_artista(artista_favorito):
    token = obtener_token_spotify()
    url = f"https://api.spotify.com/v1/search?q={artista_favorito}&type=artist&limit=1"
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(url, headers=headers)
    
    print(f"Respuesta de la API de artistas: {response.json()}")

    if response.status_code == 200:
        data = response.json()
        if data['artists']['items']:
            return data['artists']['items'][0]['id']  
        else:
            raise Exception("Artista no encontrado en Spotify")
    else:
        raise Exception(f"Error al buscar el artista: {response.status_code}")

def obtener_id_cancion(cancion_favorita):
    token = obtener_token_spotify()
    url = f"https://api.spotify.com/v1/search?q={cancion_favorita}&type=track&limit=1"
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(url, headers=headers)
    
    print(f"Respuesta de la API de canciones: {response.json()}")

    if response.status_code == 200:
        data = response.json()
        if data['tracks']['items']:
            return data['tracks']['items'][0]['id']  
        else:
            raise Exception("Canción no encontrada en Spotify")
    else:
        raise Exception(f"Error al buscar la canción: {response.status_code}")

def obtener_detalles_cancion(cancion_favorita):
    token = obtener_token_spotify()
    id_cancion = obtener_id_cancion(cancion_favorita)
    
    url = f"https://api.spotify.com/v1/tracks/{id_cancion}"
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Error al obtener detalles de la canción: {response.status_code}")

def obtener_detalles_artista(artista_favorito):
    token = obtener_token_spotify()
    id_artista = obtener_id_artista(artista_favorito)
    
    url = f"https://api.spotify.com/v1/artists/{id_artista}"
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Error al obtener detalles del artista: {response.status_code}")

# <-------- VIEWS -------->

# View para ver y crear usuarios
class view_usuarios(APIView):
    def get(self, request):
        modeloUsuario = Tabla_Usuario.objects.all() 
        serializador = Serializar_Tabla_Usuario(modeloUsuario, many=True)
        return Response(serializador.data, status=status.HTTP_200_OK)
    
    def post (self, request):
        serializador = Serializar_Tabla_Usuario(data=request.data)
        if serializador.is_valid():
            serializador.save()
            return Response(serializador.data, status=status.HTTP_201_CREATED)
        
        return Response(serializador.errors, status=status.HTTP_400_BAD_REQUEST)

# View para CRUD de usuario concreto
class view_usuario_concreto(APIView):
    def get(self, request, nombre):
        try: 
            modeloUsuario = Tabla_Usuario.objects.get(nombre=nombre)
            serializador = Serializar_Tabla_Usuario(modeloUsuario)
            return Response(serializador.data, status=status.HTTP_200_OK)
        except Tabla_Usuario.DoesNotExist:
            return Response({'error': 'Usuario no encontrado'}, status=status.HTTP_404_NOT_FOUND)
        
    def put(self, request, nombre):
        try:
            modeloUsuario = Tabla_Usuario.objects.get(nombre=nombre)
        except Tabla_Usuario.DoesNotExist:
            return Response({'error': 'Usuario no encontrado'}, status=status.HTTP_404_NOT_FOUND)

        serializador = Serializar_Tabla_Usuario(modeloUsuario, data=request.data)
        if serializador.is_valid():
            serializador.save()
            return Response(serializador.data, status=status.HTTP_200_OK)
        return Response(serializador.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, nombre):
        try:
            modeloUsuario = Tabla_Usuario.objects.get(nombre=nombre)
            modeloUsuario.delete()
            return Response({'mensaje': 'Usuario eliminado con éxito'}, status=status.HTTP_204_NO_CONTENT)
        except modeloUsuario.DoesNotExist:
            return Response({'error': 'Usuario no encontrado'}, status=status.HTTP_404_NOT_FOUND)

# <--- VIEW PARA MANEJAR FAVORITOS DE USUARIO --->
class view_favoritos_usuario(APIView):
    def post(self, request, nombre):
        try:
            usuario = Tabla_Usuario.objects.get(nombre=nombre)
        except Tabla_Usuario.DoesNotExist:
            return Response({'error': 'Usuario no encontrado'}, status=status.HTTP_404_NOT_FOUND)

        data = request.data
        artista_favorito = data.get('artista_favorito')
        cancion_favorita = data.get('cancion_favorita')

        if not artista_favorito or not cancion_favorita:
            return Response({'error': 'Artista y canción favoritos son requeridos'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            detalles_cancion = obtener_detalles_cancion(cancion_favorita)
            detalles_artista = obtener_detalles_artista(artista_favorito)
        except Exception as e:
            print(f"Error al obtener información de Spotify: {str(e)}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        album_cancion = detalles_cancion.get('album', {}).get('name', 'No disponible')
        popularidad_cancion = detalles_cancion.get('popularity', 'No disponible')
        seguidores_artista = detalles_artista.get('followers', {}).get('total', 'No disponible')
        generos_artista = detalles_artista.get('genres', [])

        print(f"Usuario: {usuario}")
        print(f"Artista favorito: {artista_favorito}")
        print(f"Canción favorita: {cancion_favorita}")
        print(f"Álbum de la canción: {album_cancion}")
        print(f"Popularidad de la canción: {popularidad_cancion}")
        print(f"Número de seguidores del artista: {seguidores_artista}")
        print(f"Géneros del artista: {generos_artista}")

        try:
            favoritos, created = Tabla_Favoritos_Usuario.objects.update_or_create(
                usuario=usuario,
                defaults={
                    'artista_favorito': artista_favorito,
                    'cancion_favorita': cancion_favorita,
                    'album_cancion': album_cancion,
                    'popularidad_cancion': popularidad_cancion,
                    'seguidores_artista': seguidores_artista,
                    'generos_artista': generos_artista
                }
            )
        except Exception as e:
            print(f"Error al guardar favoritos: {str(e)}")
            return Response({'error': 'Error al guardar favoritos'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        serializador = Serializar_Tabla_Favoritos_Usuario(favoritos)
        return Response({
            'mensaje': 'Favoritos guardados con éxito',
            'favoritos': serializador.data
        }, status=status.HTTP_201_CREATED)
    

    def get(self, request, nombre):
        try:
            usuario = Tabla_Usuario.objects.get(nombre=nombre)
            favoritos = Tabla_Favoritos_Usuario.objects.filter(usuario=usuario)
            if favoritos.exists():
                serializador = Serializar_Tabla_Favoritos_Usuario(favoritos, many=True)
                return Response(serializador.data, status=status.HTTP_200_OK)
            else:
                return Response({'mensaje': 'No se encontraron favoritos para este usuario'}, status=status.HTTP_404_NOT_FOUND)
        except Tabla_Usuario.DoesNotExist:
            return Response({'error': 'Usuario no encontrado'}, status=status.HTTP_404_NOT_FOUND)


    def put(self, request, nombre):
        try:
            usuario = Tabla_Usuario.objects.get(nombre=nombre)
            favoritos = Tabla_Favoritos_Usuario.objects.get(usuario=usuario)
        except (Tabla_Usuario.DoesNotExist, Tabla_Favoritos_Usuario.DoesNotExist):
            return Response({'error': 'Usuario o favoritos no encontrados'}, status=status.HTTP_404_NOT_FOUND)

        data = request.data
        artista_favorito = data.get('artista_favorito', favoritos.artista_favorito)
        cancion_favorita = data.get('cancion_favorita', favoritos.cancion_favorita)

        try:
            detalles_cancion = obtener_detalles_cancion(cancion_favorita)
            detalles_artista = obtener_detalles_artista(artista_favorito)
        except Exception as e:
            print(f"Error al obtener información de Spotify: {str(e)}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        favoritos.artista_favorito = artista_favorito
        favoritos.cancion_favorita = cancion_favorita
        favoritos.album_cancion = detalles_cancion.get('album', {}).get('name', 'No disponible')
        favoritos.popularidad_cancion = detalles_cancion.get('popularity', 'No disponible')
        favoritos.seguidores_artista = detalles_artista.get('followers', {}).get('total', 'No disponible')
        favoritos.generos_artista = detalles_artista.get('genres', [])
        favoritos.save()

        serializador = Serializar_Tabla_Favoritos_Usuario(favoritos)
        return Response(serializador.data, status=status.HTTP_200_OK)

    def delete(self, request, nombre):
        try:
            usuario = Tabla_Usuario.objects.get(nombre=nombre)
            favoritos = Tabla_Favoritos_Usuario.objects.get(usuario=usuario)
            favoritos.delete()
            return Response({'mensaje': 'Favoritos eliminados con éxito'}, status=status.HTTP_204_NO_CONTENT)
        except (Tabla_Usuario.DoesNotExist, Tabla_Favoritos_Usuario.DoesNotExist):
            return Response({'error': 'Usuario o favoritos no encontrados'}, status=status.HTTP_404_NOT_FOUND)