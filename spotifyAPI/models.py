from django.db import models

# Tabla para usuarios
class Tabla_Usuario(models.Model):
    nombre = models.CharField(max_length=200)
    email = models.EmailField(unique=True)

    def __str__(self):
        return self.nombre
    

# Tabla para preferencias musicales del usuario
class Tabla_Favoritos_Usuario(models.Model):
    usuario = models.ForeignKey(Tabla_Usuario, on_delete=models.CASCADE, related_name="preferencias")
    artista_favorito = models.CharField(max_length=200)
    cancion_favorita = models.CharField(max_length=200)
    album_cancion = models.CharField(max_length=200, blank=True, null=True)
    popularidad_cancion = models.IntegerField(blank=True, null=True)
    seguidores_artista = models.IntegerField(blank=True, null=True)
    generos_artista = models.JSONField(default=list, blank=True, null=True)
    
    def __str__(self):
        return f"{self.artista_favorito} - {self.cancion_favorita} ({self.usuario.nombre})"
    

