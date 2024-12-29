from django.db import models
from django.db.models import Value, F, Case, When
from django.db.models.functions import Concat, Substr, StrIndex
from django.contrib.auth.models import User
from storages.backends.s3boto3 import S3Boto3Storage
from datetime import datetime
import mutagen
import math
import os

# Create your models here.
def albums_directory(instance, filename):
    now = datetime.now()
    path = 'albums/'
    name = now.strftime('%d_%m_%Y-%H_%M_%S') + filename
    return path + name

def profileImg_directory(instance, filename):
    now = datetime.now()
    path = 'profile/'
    name = now.strftime('%d_%m_%Y-%H_%M_%S') + filename
    return path + name

def coverImg_directory(instance, filename):
    now = datetime.now()
    path = 'covers/'
    name = now.strftime('%d_%m_%Y-%H_%M_%S') + filename
    return path + name

class Profile(models.Model):
    profileImg = models.ImageField(upload_to=profileImg_directory, null=True, blank=True)
    coverImg = models.ImageField(upload_to=coverImg_directory, null=True, blank=True)
    name = models.CharField(max_length=100)
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=None)

    def __str__(self):
        return self.name

class Artist(models.Model):
    profileImg = models.ImageField(upload_to=profileImg_directory,null=True, blank=True)
    coverImg = models.ImageField(upload_to=coverImg_directory, null=True, blank=True)
    name = models.CharField(max_length=100)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return self.name
    
class Album(models.Model):
    img = models.ImageField(upload_to=albums_directory, blank=True, null=True)
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE, blank=True, null=True)
    name = models.CharField(max_length=200)
    album_type = models.IntegerField(default=0) # 0 = ALBUM | 1 = EP
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return self.name
    
# MUSICS
def music_img_directory(instance, filename):
    now = datetime.now()
    path = 'music_covers/'
    name = now.strftime('%d_%m_%Y-%H_%M_%S') + filename
    return path + name

def music_directory(instance, filename):
    now = datetime.now()
    path = 'musics/'
    name = now.strftime('%d_%m_%Y-%H_%M_%S') + filename
    return path + name
    
class Music(models.Model):
    img = models.ImageField(upload_to=music_img_directory, null=True, blank=True)
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    song = models.FileField(upload_to=music_directory, null=True, blank=True)
    album = models.ForeignKey(Album, on_delete=models.CASCADE, null=True, blank=True)
    duration = models.CharField(max_length=20, null=True, blank=True)
    views = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return self.name
    
    @property
    def imgUrl(self):
        if self.img.name == '':
            return self.album.img.url
        else:
            return self.img.url
    
class Genre(models.Model):
    name = models.CharField(max_length=100)
    music = models.ManyToManyField(Music)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return self.name
    
class List(models.Model):
    name = models.CharField(max_length=100)
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='lists')
    musics = models.ManyToManyField(Music, through='L_musics')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name
    
    @property
    def getImg(self):
        try:
            return self.musics.all().first().imgUrl
        except Exception as e: 
            return ''
    
class L_musics(models.Model):
    list_music = models.ForeignKey(Music, on_delete=models.CASCADE)
    list_musics = models.ForeignKey(List, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
class Liked_lists(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    lists = models.ManyToManyField(List, through='L_list')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self) -> str:
        return self.profile.name
    
class L_list(models.Model):
    list_object = models.ForeignKey(List, on_delete=models.CASCADE)
    liked_lists = models.ForeignKey(Liked_lists, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
class Liked_musics(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    musics = models.ManyToManyField(Music, through='LM_musics')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.profile.name
    
class LM_musics(models.Model):
    liked_music = models.ForeignKey(Music, on_delete=models.CASCADE)
    liked_musics = models.ForeignKey(Liked_musics, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
class Liked_albums(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    albums = models.ManyToManyField(Album, through='LA_albums')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.profile.name
    
class LA_albums(models.Model):
    liked_album = models.ForeignKey(Album, on_delete=models.CASCADE)
    liked_albums = models.ForeignKey(Liked_albums, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
class Followed_artists(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    artists = models.ManyToManyField(Artist, through='FA_artist')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.profile.name
    
class FA_artist(models.Model):
    liked_artist = models.ForeignKey(Artist, on_delete=models.CASCADE)
    liked_artists = models.ForeignKey(Followed_artists, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)