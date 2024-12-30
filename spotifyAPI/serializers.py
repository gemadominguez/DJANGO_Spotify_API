from rest_framework import serializers
from .models import Tabla_Usuario, Tabla_Favoritos_Usuario

class Serializar_Tabla_Favoritos_Usuario(serializers.ModelSerializer):
    class Meta:
        model = Tabla_Favoritos_Usuario
        fields = ['artista_favorito', 'cancion_favorita', 'album_cancion', 'popularidad_cancion', 'seguidores_artista', 'generos_artista']

class Serializar_Tabla_Usuario(serializers.ModelSerializer):
    favoritos = serializers.SerializerMethodField()

    class Meta:
        model = Tabla_Usuario
        fields = ['nombre', 'email', 'favoritos']

    def get_favoritos(self, obj):
        favoritos = Tabla_Favoritos_Usuario.objects.filter(usuario=obj)
        return Serializar_Tabla_Favoritos_Usuario(favoritos, many=True).data
    

    