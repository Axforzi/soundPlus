from django.contrib import admin
from .models import Artist, Music, Album, Genre, Profile, Liked_musics, Liked_albums, Followed_artists, List

# Register your models here.
admin.site.register(Artist)
admin.site.register(Music)
admin.site.register(Album)
admin.site.register(Genre)
admin.site.register(Profile)
admin.site.register(Liked_musics)
admin.site.register(Liked_albums)
admin.site.register(Followed_artists)
admin.site.register(List)
