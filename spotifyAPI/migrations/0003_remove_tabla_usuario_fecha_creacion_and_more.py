# Generated by Django 5.1.4 on 2024-12-30 00:54

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('spotifyAPI', '0002_rename_tabla_preferenciamusical_tabla_favoritosusuario_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='tabla_usuario',
            name='fecha_creacion',
        ),
        migrations.CreateModel(
            name='Tabla_Favoritos_Usuario',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('artista_favorito', models.CharField(max_length=200)),
                ('cancion_favorita', models.CharField(max_length=200)),
                ('top_5_recomendaciones', models.JSONField(blank=True, null=True)),
                ('usuario', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='preferencias', to='spotifyAPI.tabla_usuario')),
            ],
        ),
        migrations.DeleteModel(
            name='Tabla_FavoritosUsuario',
        ),
    ]
