from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, StreamingHttpResponse
from .form import FormLogin, FormSignup, FormAlbums, FormMusics, FormEditProfile, FormEditArtistAccount
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Value
from .models import Album, Artist, Music, Profile, Liked_musics, Liked_albums, Liked_lists, Followed_artists, List
from django.db.models import F, Count, Q, Subquery, OuterRef
from django.db.models.functions import Coalesce
from django.db.models.functions import ExtractYear
from django.utils.cache import add_never_cache_headers
import os
import requests
from itertools import chain
from django.conf import settings
from django.http import Http404
from django.views.static import serve

def get_library(request) -> dict:
    profile = request.user.profile_set.first()
    
    liked_albums = (
        Liked_albums.objects.filter(profile=profile)
        .annotate(
            item_id=F('albums__id'),
            name=F('albums__name'),
            img=F('albums__img'),
            added_at=F('la_albums__created_at'),
            type=Value('album')
        )
        .values('item_id', 'name', 'img', 'type', 'added_at')
        .exclude(item_id=None)
    )
    
    follow_artist = (
        Followed_artists.objects.filter(profile=profile)
        .annotate(
            item_id=F('artists__id'),
            name=F('artists__name'),
            img=F('artists__profileImg'),
            added_at=F('fa_artist__created_at'),
            type=Value('artist')
        )
        .values('item_id', 'name', 'img', 'type', 'added_at')
        .exclude(item_id=None)
    )
    
    list_objects = (
        List.objects.filter(profile=profile)
        .annotate(
            item_id=F('id'),
            list_name=F('name'),
            img=Coalesce(
                Subquery(Music.objects.filter(list=OuterRef('item_id'), img__isnull=False).values('img').exclude(img__exact='')[:1]),
                Subquery(Album.objects.filter(music__list=OuterRef('item_id')).values('img')[:1])
            ),
            added_at=F('created_at'),
            type=Value('list')
        )
        .values('item_id', 'list_name', 'img', 'type', 'added_at')
        .exclude(item_id=None)
    )
    
    liked_lists = (
        Liked_lists.objects.filter(profile=profile)
        .annotate(
            item_id=F('lists__id'),
            list_name=F('lists__name'),
            img=Coalesce(
                Subquery(Music.objects.filter(list=OuterRef('item_id'), img__isnull=False).values('img').exclude(img__exact='')[:1]),
                Subquery(Album.objects.filter(music__list=OuterRef('item_id')).values('img')[:1])
            ),
            added_at=F('l_list__created_at'),
            type=Value('list')
        )
        .values('item_id', 'list_name', 'img', 'type', 'added_at')
        .exclude(item_id=None)
    )
    
    combined_query = liked_albums.union(follow_artist, list_objects, liked_lists).order_by('-added_at')
    return {'library_elements': combined_query}


def index(request):
    if request.htmx:
        context = {
            "artists": Artist.objects.all(),
            "albums": Album.objects.all().exclude(name='Ninguno'),
            "musics": Music.objects.all(),
        }
        return render(request, "index.html#index", context)
    else:
        if request.user.is_authenticated:
            context = {
                "login": FormLogin,
                "artists": Artist.objects.all(),
                "albums": Album.objects.all().exclude(name='Ninguno'),
                "musics": Music.objects.all()
            }
            context.update(get_library(request))
            return render(request, "index.html", context)
        
        else:
            context = {
                "login": FormLogin,
                "artists": Artist.objects.all(),
                "albums": Album.objects.all().exclude(name='Ninguno'),
                "musics": Music.objects.all()
            }
            return render(request, "index.html", context)
            


def login_view(request):
    if request.method == "POST":
        form = FormLogin(request.POST)
        if form.is_valid():
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password"]
            user = get_user_model().objects.filter(username=username).first()

            if user is not None:
                userAuthentication = authenticate(
                    request, username=username, password=password
                )
                if userAuthentication is not None:
                    login(request, user)
                    return redirect(request.META.get("HTTP_REFERER"))

                # WRONG PASSWORD
                else:
                    messages.error(
                        request, "Contraseña incorrecta!!", extra_tags="password_err"
                    )
                    return redirect(request.META.get("HTTP_REFERER"), {"login": form})
            else:
                # THIS USERNAME DOES NOT EXIST
                messages.error(
                    request,
                    "El usuario o correo no esta registrado!!",
                    extra_tags="user_err",
                )
                return redirect(request.META.get("HTTP_REFERER"), {"login": form})

    else:
        messages.success(request, "modalShow")
        return redirect("index")


def signup(request):
    if request.method == "POST":
        form = FormSignup(request.POST)
        if form.is_valid():
            user = form.save()
            profile = Profile(name=user.first_name, user=user)
            profile.save()

            return redirect("index")
        else:
            if (form.has_error('password2')):
                for error in form.errors.as_data()['password2']:
                    if(error.code == 'password_too_similar'):
                        messages.error(request, 'La contraseña es muy similar al nombre de usuario o dirección de correo electrónico')
                    elif(error.code == 'password_mismatch'):
                        messages.error(request, 'Las contraseñas no coinciden')
                    elif(error.code == 'password_too_common'):
                        messages.error(request, 'La contraseña es muy común')
                    elif(error.code == 'password_enterily_numeric'):
                        messages.error(request, 'La contraseña no puede ser completamente numérica')
                    elif(error.code == 'password_too_short'):
                        messages.error(request, 'La contraseña es muy corta')

            return render(request, "pages/signup.html", {"signup": form})
    else:
        return render(request, "pages/signup.html", {"signup": FormSignup})


def logout_view(request):
    if request.user.is_authenticated:
        logout(request)
        return redirect("index")
    else:
        return redirect("login")

def profile_view(request, id):
    if request.htmx:
        profile = Profile.objects.filter(id=id).first()
        lists = List.objects.filter(profile=profile)
        
        context = {'profile': profile,
                   'lists': lists}
        return render(request, "pages/profile.html#profile", context)
    else:
        profile = Profile.objects.filter(id=id).first()
        lists = List.objects.filter(profile=profile)
        
        context = {'profile': profile,
                   'lists': lists}
        context.update(get_library(request))
        return render(request, "pages/profile.html", context)

@login_required    
def myprofile_view(request):
    if request.htmx:
        profile = request.user.profile_set.first()
        form = FormEditProfile(instance=profile)
        lists = List.objects.filter(profile=profile)
        
        context = {'formProfile': form,
                   'profile': profile,
                   'lists': lists}
        return render(request, "pages/profile.html#profile", context)
    else:
        profile = request.user.profile_set.first()
        form = FormEditProfile(instance=profile)
        lists = List.objects.filter(profile=profile)
        
        context = {'formProfile': form, 
                   'profile': profile,
                   'lists': lists}
        context.update(get_library(request))
        return render(request, "pages/profile.html", context)
    
@login_required
def profile_save(request):
    if request.method == "POST":
        profile = request.user.profile_set.first()
        form = FormEditProfile(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()

            return render(request, "pages/profile.html#profile", { 'formProfile': form, 'profile': profile, "updateHeader": True })

@login_required
def create_artist(request):
    if request.method == 'POST':
        form = FormEditArtistAccount(request.POST, request.FILES)
        if form.is_valid():
            artist = form.save(commit=False)
            artist.user = request.user
            artist.save()

            response = HttpResponse('')
            response['HX-Redirect'] = '/'
            return response
        else:
            return render(request, 'pages/create-artist.html#form', { 'formProfile': form })
    else:
        if request.htmx:
            return render(request, 'pages/create-artist.html#page', { 'formProfile': FormEditArtistAccount})
        else:
            context = {
                'login': FormLogin,
                'formProfile': FormEditArtistAccount
            }
            return render(request, 'pages/create-artist.html', context)

@login_required
def artist_account_view(request):
    if request.htmx:
        artist = request.user.artist_set.first()
        form = FormEditArtistAccount(instance=artist)
        musics = Music.objects.filter(artist=artist).order_by('-views')
        likedMusics = Music.objects.filter(artist=artist).annotate(likes=Count('liked_musics')).order_by('-likes')
        albums = Album.objects.filter(artist=artist).exclude(name='Ninguno').annotate(likes=Count('liked_albums')).order_by('-likes')
        
        context = { 'formProfile': form, 
                    'artist': artist,
                    'musics': musics,
                    "likedMusics": likedMusics,
                    "albums": albums}
        return render(request, "pages/artist-account.html#profile", context)
    else:
        artist = request.user.artist_set.first()
        form = FormEditArtistAccount(instance=artist)
        musics = Music.objects.filter(artist=artist).order_by('-views')
        likedMusics = Music.objects.filter(artist=artist).annotate(likes=Count('liked_musics')).order_by('-likes')
        albums = Album.objects.filter(artist=artist).exclude(name='Ninguno').annotate(likes=Count('liked_albums')).order_by('-likes')
        
        context = { 'formProfile': form, 
                    'artist': artist,
                    'musics': musics,
                    "likedMusics": likedMusics,
                    "albums": albums}
        context.update(get_library(request))
        return render(request, "pages/artist-account.html", context)

@login_required
def artist_account_save(request):
    if request.method == 'POST':
        artist = Artist.objects.filter(user=request.user.id).first()
        form = FormEditArtistAccount(request.POST, request.FILES, instance=artist)
        if form.is_valid():
            form.save()
            
            musics = Music.objects.filter(artist=artist).order_by('-views')
            context = { 'formProfile': form, 
                        'artist': artist,    
                        'musics': musics,
                        "updateElement": True}
            return render(request, "pages/artist-account.html#profile", context)

def artist_view(request, artist_name):
    context = {}
    
    # GET DATA
    try:
        artist = get_object_or_404(Artist, name = artist_name)
        artist_music = artist.music_set.all().order_by('-views')[:5]
        artist_albums = artist.album_set.filter(album_type=0).all().order_by('-created_at')
        
        # GET EP's AND SINGLES
        artist_ep = artist.album_set.filter(album_type=1).all().values('name', 'img', 'created_at', artist_name=F('artist__name')).annotate(model_type=Value('Album'))
        artist_singles = artist.music_set.filter(album__name='Ninguno').all().values('name', 'img', 'created_at', artist_name=F('artist__name')).annotate(model_type=Value('Music'))
        artist_ep_singles = artist_singles.union(artist_ep).order_by('-created_at')
        
        context.update({
                'artist': artist,
                'artist_music': artist_music,
                'artist_albums': artist_albums,
                'artist_ep_singles': artist_ep_singles
        })
    except Http404:
        if request.htmx:
            return render(request, '404.html#error_404')
        else:
            if request.user.is_authenticated:
                context.update(get_library(request))
            else:
                context.update({'login': FormLogin})
                
            return render(request, '404.html', context, status=404)
    
    # GET REPONSE
    if request.htmx:
        if request.user.is_authenticated:
            # CHECK FOLLOW
            profile = request.user.profile_set.first()
            follow_exist = Followed_artists.objects.filter(profile=profile, artists=artist).exists()
            context.update({'follow': follow_exist})
        
        # RESPONSE
        return render(request, "pages/artist.html#artist-content", context)
    else:
        if request.user.is_authenticated: 
            profile = request.user.profile_set.first()
            
            # CHECK FOLLOW
            follow_exist = Followed_artists.objects.filter(profile=profile, artists=artist).exists()
            context.update({ 'follow': follow_exist })
            context.update(get_library(request))
        
        else:
            context.update({ 'login': FormLogin })
        
        # RESPONSE
        return render(request, "pages/artist.html", context)
    
def album_view(request, artist_name, album_name):
    context = {}
    
    # GET DATA OR ERROR
    try:
        artist = get_object_or_404(Artist, name = artist_name)
        album = get_object_or_404(Album, artist = artist, name = album_name)
        context.update({ 
                            'artist': artist, 
                            'album': album, 
        })
    except Http404:
        if request.htmx:
            return render(request, '404.html#error_404')
        else:
            if request.user.is_authenticated:
                context.update(get_library(request))
            else:
                context.update({'login': FormLogin})
                
            return render(request, '404.html', context, status=404)
    
    if request.htmx:
        # CHECK LIKE
        if request.user.is_authenticated:
            profile = request.user.profile_set.first()
            like_exist = Liked_albums.objects.filter(profile=profile, albums=album).exists()
            context.update({ 'liked': like_exist})
            
        return render(request, "pages/album.html#album", context)
    
    else:
        # CHECK LIKE 
        if request.user.is_authenticated:
            profile = request.user.profile_set.first()
            like_exist = Liked_albums.objects.filter(profile=profile, albums=album).exists()
            context.update({ 'liked': like_exist})
            context.update(get_library(request))
        else:
            context.update({ 'login': FormLogin})
        
        return render(request, "pages/album.html", context)
        
        
def single_view(request, artist_name, single_name):
    context = {}
    
    try:
        artist = get_object_or_404(Artist, name = artist_name)
        music = get_object_or_404(Music, artist=artist, name = single_name)
        context.update({
            'artist': artist,
            'music': music
        })
    except Http404:
        if request.htmx:
            return render(request, '404.html#error_404')
        else:
            if request.user.is_authenticated:
                context.update(get_library(request))
            else:
                context.update({'login': FormLogin})
                
            return render(request, '404.html', context, status=404)
    
    if request.htmx:
        return render(request, "pages/single.html#single", context)
    
    else:
        if request.user.is_authenticated:
            context.update(get_library(request))
        else:
            context.update({ 'login': FormLogin })
        
        return render(request, "pages/single.html", context)
        
def discography_view(request, artist_name):
    context = {}
    
    # GET DATA
    try:
        artist = get_object_or_404(Artist, name = artist_name)
        albums = artist.album_set.exclude(album_type=1).annotate(year=ExtractYear('created_at')).order_by('-created_at')
        
        # GET EP's AND SINGLES
        artist_ep = artist.album_set.filter(album_type=1).all().values('name', 'img', 'created_at', artist_name=F('artist__name')).annotate(model_type=Value('Album'), year=ExtractYear('created_at'))
        artist_singles = artist.music_set.filter(album__name='Ninguno').all().values('name', 'img', 'created_at', artist_name=F('artist__name')).annotate(model_type=Value('Music'), year=ExtractYear('created_at'))
        ep_singles = artist_singles.union(artist_ep).order_by('-created_at')
        
        context.update({
            'artist': artist, 
            'albums': albums,
            'ep_singles': ep_singles
        })
    except Http404:
        if request.htmx:
            return render(request, '404.html#error_404')
        else:
            if request.user.is_authenticated:
                context.update(get_library(request))
            else:
                context.update({'login': FormLogin})
                
            return render(request, '404.html', context, status=404)
    
    # GET RESPONSE
    if request.htmx:
        return render(request, "pages/discography.html#discography", context)
    
    else:
        if request.user.is_authenticated:
            context.update(get_library(request))
        else:
            context.update({'login': FormLogin})
        
        return render(request, "pages/discography.html", context)
        
        
def section_view(request, section):
    context = {}
    
    # ADD INFO TO CONTEXT
    if section == 'artists':
        artists = Artist.objects.annotate(followers=Count('followed_artists')).order_by('-followers')
        context = {'objects': artists,
                    'section': section }
    
    elif section == 'albums':
        albums = Album.objects.exclude(name='Ninguno').annotate(likes=Count('liked_albums')).order_by('-likes')
        context = {'objects': albums,
                    'section': section }
    
    elif section == 'songs':
        musics = Music.objects.order_by('-views')
        context = {'objects': musics,
                    'section': section }
    else:
        if request.htmx:
            return render(request, '404.html#error_404')
        else:
            return render(request, '404.html', context=get_library(request), status=404)
    
    # GET RESPONSE
    if request.htmx:
        return render(request, 'pages/section.html#section', context)
    
    else:
        if request.user.is_authenticated:
            context.update(get_library(request))
        else:
            context.update({'login': FormLogin})

        return render(request, 'pages/section.html', context)
        
    
def play_album(request, id):
    context = {}
    if request.htmx:
        currentMusic =  request.GET.get('currentMusic', None)
        if 'random' in request.GET:
            music = Music.objects.filter(id=currentMusic)
            musics_albums = Album.objects.filter(id=id).first().music_set.all().exclude(pk__in=music).order_by('?')
            
            if musics_albums.exists():
                musics = list(chain(music, musics_albums))
                context.update({ 'musics_queue': musics, 'is_album': id, 'random': True })
            else:
                context.update({ 'musics_queue': music, 'is_album': id, 'random': True })
                
        else:
            music = Music.objects.filter(id=currentMusic)
            musics_albums = Album.objects.filter(id=id).first().music_set.exclude(pk__in=music).all()
            
            if musics_albums.exists():
                musics = list(chain(music, musics_albums))
                context.update({ 'musics_queue': musics, 'is_album': id })
            else:
                context.update({ 'musics_queue': music, 'is_album': id })
                
            
        return render(request, 'modal.html#tableSongs', context)

def play_artist(request, artist_name):
    context = {}
    
    if request.htmx:
        currentMusic = request.GET.get('currentMusic', None)
        if 'random' in request.GET:
            music = Music.objects.filter(id=currentMusic)
            musics_artist = Artist.objects.filter(name=artist_name).first().music_set.all().exclude(pk__in=music).order_by('?')
            
            if musics_artist.exists():    
                musics = list(chain(music, musics_artist))
                context.update({ 'musics_queue': musics, 'is_artist': artist_name, 'random': True})
            else:
                context.update({ 'musics_queue': music, 'is_artist': artist_name, 'random': True})

        else:
            music = Music.objects.filter(id=currentMusic)
            musics_artist = Artist.objects.filter(name=artist_name).first().music_set.all().exclude(pk__in=music)
            
            if musics_artist.exists():    
                musics = list(chain(music, musics_artist))
                context.update({ 'musics_queue': musics, 'is_artist': artist_name })
            else:
                context.update({ 'musics_queue': music, 'is_artist': artist_name })
            
        return render(request, 'modal.html#tableSongs', context)
    
def play_music(request, id):
    context = {}
    
    if request.htmx:
        currentMusic = request.GET.get('currentMusic', None)
        if 'random' in request.GET:
            music = Music.objects.filter(id=currentMusic)
            musics_by_artist = Music.objects.filter(artist=music.first().artist).exclude(pk__in=music).order_by('?')
            
            if musics_by_artist.exists():    
                musics = list(chain(music, musics_by_artist))
                context.update({ 'musics_queue': musics, 'is_music': id, 'random': True })
            else:
                context.update({ 'musics_queue': music, 'is_music': id, 'random': True })
                
        else:
            id_music = currentMusic if currentMusic != None else id
            music = Music.objects.filter(id=id_music)
            musics_by_artist = Music.objects.filter(artist=music.first().artist).exclude(pk__in=music)
            
            if musics_by_artist.exists():    
                musics = list(chain(music, musics_by_artist))
                context.update({ 'musics_queue': musics, 'is_music': id })
            else:
                context.update({ 'musics_queue': music, 'is_music': id })
                
        return render(request, 'modal.html#tableSongs', context)
    
def play_music_on_album(request, id):
    context = {}
    
    if request.htmx:
        currentMusic = request.GET.get('currentMusic', None)
        if 'random' in request.GET:
            music = Music.objects.filter(id=currentMusic)
            album_musics = music.first().album.music_set.exclude(pk__in=music)
            artist_musics = music.first().artist.music_set.exclude(pk__in=album_musics|music)
            
            if artist_musics.exists():    
                musics = album_musics.union(artist_musics).order_by('?')
                musics = list(chain(music, musics))
                context.update({ 'musics_queue': musics, 'is_music_on_album': id, 'random': True })
            else:
                musics = list(chain(music, album_musics.order_by('?')))
                context.update({ 'musics_queue': musics, 'is_music_on_album': id, 'random': True })
        else:
            id_music = currentMusic if currentMusic != None else id
            music = Music.objects.filter(id=id_music)
            album_musics = music.first().album.music_set.exclude(pk__in=music)
            artist_musics = music.first().artist.music_set.exclude(pk__in=album_musics|music)
            
            if artist_musics.exists():
                musics = album_musics.union(artist_musics)
                musics = list(chain(music, musics))
                context.update({ 'musics_queue': musics, 'is_music_on_album': id })
            else:
                musics = list(chain(music, album_musics))
                context.update({ 'musics_queue': musics, 'is_music_on_album': id })
            
        return render(request, 'modal.html#tableSongs', context)

def play_liked_musics(request):
    context = {}
    profile = request.user.profile_set.first()
    currentMusic = request.GET.get('currentMusic', None)
    if 'random' in request.GET:
        music = Music.objects.filter(id=currentMusic)
        likedMusics = Liked_musics.objects.filter(profile=profile).first().musics.all().exclude(pk__in=music).order_by('?')
        
        if likedMusics.exists():    
            musics = list(chain(music, likedMusics))
            context.update({ 'musics_queue': musics, 'is_liked_musics': True, 'random': True })
        else:
            context.update({ 'musics_queue': music, 'is_liked_musics': True, 'random': True })
    else:
        music = Music.objects.filter(id=currentMusic)
        likedMusics = Liked_musics.objects.filter(profile=profile).first().musics.all().exclude(pk__in=music).order_by('-lm_musics__created_at')
        
        if likedMusics.exists():    
            musics = list(chain(music, likedMusics))
            context.update({ 'musics_queue': musics, 'is_liked_musics': True })
        else:
            context.update({ 'musics_queue': music, 'is_liked_musics': True })
        
    return render(request, 'modal.html#tableSongs', context)

def play_liked_music(request, id):
    context = {}
    profile = request.user.profile_set.first()
    currentMusic = request.GET.get('currentMusic', None)
    if 'random' in request.GET:
        music = Liked_musics.objects.filter(profile=profile).first().musics.filter(id=currentMusic)
        likedMusics = Liked_musics.objects.filter(profile=profile).first().musics.all().exclude(pk__in=music).order_by('?')
        
        if likedMusics.exists():
            musics = list(chain(music, likedMusics))
            context.update({ 'musics_queue': musics, 'is_liked_music': id, 'random': True })
        else:
            context.update({ 'musics_queue': music, 'is_liked_music': id, 'random': True })
    else:
        id_music = currentMusic if currentMusic != None else id
        music = Liked_musics.objects.filter(profile=profile).first().musics.filter(id=id_music)
        likedMusics = Liked_musics.objects.filter(profile=profile).first().musics.all().exclude(pk__in=music).order_by('-lm_musics__created_at')
        
        if likedMusics.exists():
            musics = list(chain(music, likedMusics))
            context.update({ 'musics_queue': musics, 'is_liked_music': id })
        else:
            context.update({ 'musics_queue': music, 'is_liked_music': id })
        
    return render(request, 'modal.html#tableSongs', context)

def play_list(request, id):
    context = {}
    currentMusic = request.GET.get('currentMusic', None)
    if 'random' in request.GET:
        music = Music.objects.filter(id=currentMusic)
        list_musics = List.objects.filter(id=id).first().musics.all().exclude(pk__in=music).order_by('?')
        
        if list_musics.exists():
            musics = list(chain(music, list_musics))
            context.update({ 'musics_queue': musics, 'is_list': id, 'random': True })
        else:
            context.update({ 'musics_queue': music, 'is_list': id, 'random': True })
    else:
        id_music = currentMusic if currentMusic != None else id
        music = Music.objects.filter(id=id_music)
        list_musics = List.objects.filter(id=id).first().musics.all().exclude(pk__in=music).order_by('l_musics__created_at')
        
        if list_musics.exists():
            musics = list(chain(music, list_musics))
            context.update({ 'musics_queue': musics, 'is_list': id })
        else:
            context.update({ 'musics_queue': music, 'is_list': id })
        
    return render(request, 'modal.html#tableSongs', context)
    
def play_music_on_list(request, id_list, id_music):
    context = {}
    currentMusic = request.GET.get('currentMusic', None)
    if 'random' in request.GET:
        music = Music.objects.filter(id=currentMusic)
        list_musics = List.objects.filter(id=id_list).first().musics.exclude(pk__in=music).order_by('?')
        
        if list_musics.exists():
            musics = list(chain(music, list_musics))
            context.update({ 'musics_queue': musics, 'is_list_music': True, 'id_list': id_list, 'id_music': id_music, 'random': True})
        else:
            context.update({ 'musics_queue': music, 'is_list_music': True, 'id_list': id_list, 'id_music': id_music, 'random': True})
    else:
        id_music = currentMusic if currentMusic != None else id_music
        music = Music.objects.filter(id=id_music)
        list_musics = List.objects.filter(id=id_list).first().musics.exclude(pk__in=music).order_by('l_musics__created_at')
        
        if list_musics.exists():
            musics = list(chain(music, list_musics))
            context.update({ 'musics_queue': musics, 'is_list_music': True, 'id_list': id_list, 'id_music': id_music })
        else:
            context.update({ 'musics_queue': music, 'is_list_music': True, 'id_list': id_list, 'id_music': id_music })
    
    return render(request, 'modal.html#tableSongs', context)

def serve_music(request, id_music):
    music = get_object_or_404(Music, id=id_music)
    
    # SONG EXIST
    if not music.song:
        raise Http404("Archivo no encontrado.")
    
    file_url = f"https://{os.getenv('SUPABASE_PROJECT_URL')}/storage/v1/object/public/{os.getenv('SUPABASE_BUCKET_NAME')}/{music.song.name}"
    file_path = music.song.name
    
    #UPDATE VIEWS
    music.views = F('views') + 1
    music.save(update_fields=['views'])
    
    # PARTIAL REQUEST
    headers = {}
    if 'HTTP_RANGE' in request.META:  
        headers['Range'] = request.META['HTTP_RANGE']

    try:
        response = requests.get(file_url, headers=headers, stream=True)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        raise Http404(f"No se pudo obtener el archivo: {str(e)}")

    # CREATE RESPONSE
    django_response = StreamingHttpResponse(
        streaming_content=response.iter_content(chunk_size=8192),
        content_type=response.headers.get('Content-Type', 'application/octet-stream')
    )
    django_response['Content-Length'] = response.headers.get('Content-Length', '0')
    if 'Content-Range' in response.headers:
        django_response['Content-Range'] = response.headers['Content-Range']

    django_response['Accept-Ranges'] = 'bytes'
    django_response['Content-Disposition'] = f'inline; filename="{file_path.split("/")[-1]}"'
    
    # NO CACHE
    add_never_cache_headers(django_response)
    return django_response

def add_queue(request, id):
    if request.htmx:
        music = Music.objects.filter(id=id).first()
        return render(request, 'modal.html#queueElement', { 'music': music })
    
def about(request):
    return HttpResponse("About")

def search(request):
    context = {}
    if len(request.GET) != 0:
        data = request.GET['search']
        
        if 'filter' in request.GET:
            filter = request.GET['filter']
            
            if filter == 'artists':
                artists = Artist.objects.filter(Q(name__icontains=data) | Q(album__name__icontains=data) | Q(music__name__icontains=data)).order_by('-name').distinct()
                context.update({ 'artists': artists, 'btnFilter': 'artists', 'results': True, 'search': data })
            
            if filter == 'albums':
                albums = Album.objects.filter(Q(name__icontains=data) | Q(artist__name__icontains= data) | Q(music__name__icontains=data)).exclude(name='Ninguno').order_by('-name').distinct()
                context.update({ 'albums': albums , 'btnFilter': 'albums', 'results': True, 'search': data })
                
            if filter == 'songs':
                musics = Music.objects.filter(Q(name__icontains=data) | Q(album__name__icontains=data) | Q(artist__name__icontains= data)).order_by('-name').distinct()
                context.update({ 'musics': musics, 'btnFilter': 'songs', 'results': True, 'search': data })
                
            if filter == 'lists':
                list_objects = List.objects.filter(Q(name__icontains=data) | Q(musics__name__icontains=data) | Q(musics__artist__name__icontains=data)).order_by('-name').distinct()
                context.update({ 'lists': list_objects, 'btnFilter': 'lists', 'results': True, 'search': data })
                
            if filter == 'profiles':
                profiles = Profile.objects.filter(name__icontains=data).order_by('-name')
                context.update({ 'profiles': profiles, 'btnFilter': 'profiles', 'results': True, 'search': data })
                
        else:
            artists = Artist.objects.filter(Q(name__icontains=data) | Q(album__name__icontains=data) | Q(music__name__icontains=data)).order_by('-name').distinct()[:4]
            albums = Album.objects.filter(Q(name__icontains=data) | Q(artist__name__icontains= data) | Q(music__name__icontains=data)).exclude(name='Ninguno').order_by('-name').distinct()[:4]
            musics = Music.objects.filter(Q(name__icontains=data) | Q(album__name__icontains=data) | Q(artist__name__icontains= data)).order_by('-name').distinct()[:4]
            list_objects = List.objects.filter(Q(name__icontains=data) | Q(musics__name__icontains=data) | Q(musics__artist__name__icontains=data)).order_by('-name').distinct()[:4]
            profiles = Profile.objects.filter(name__icontains=data).order_by('-name')[:4]
            
            context = {
                'artists': artists,
                'albums': albums,
                'musics': musics,
                'lists': list_objects,
                'profiles': profiles,
                'search': data,
                'results': True,
                'btnFilter': 'all',
            }
        
        if request.htmx:
            return render(request, 'pages/search.html#search', context)
        else:
            if request.user.is_authenticated:
                context.update(get_library(request))
            else:
                context.update({'login': FormLogin})
                
            return render(request, 'pages/search.html', context=context)
    else:
        if request.htmx:
            return render(request, 'pages/search.html#search')
        else:
            if request.user.is_authenticated:
                context.update(get_library(request))
            else:
                context.update({'login': FormLogin})
                
            return render(request, 'pages/search.html', context=context)

def search_results(request, search):
    pass

def search_artist(request, entry):
    pass
    
@login_required
def like_music(request, id):
    if request.htmx:
        profile = request.user.profile_set.first()
        added=False
        
        # CHECK IF THERE'S A REGISTER
        liked_musics = Liked_musics.objects.filter(profile=profile)
        if liked_musics.exists():
            musics = liked_musics.first().musics
            
            # CHECK IF ADD OR REMOVE LIKE
            if musics.filter(id=id).exists():
                musics.remove(id)
            else:
                musics.add(id)
                added=True
            
        else:
            # CREATE REGISTER
            liked_music = Liked_musics(profile=profile)
            liked_music.save()
            
            # ADD LIKED SONG
            liked_musics = Liked_musics.objects.filter(profile=profile).first()
            liked_musics.musics.add(id)
            added=True
            
        return render(request, 'list.html#likeElement', {"musicId": id, "added":added})

@login_required   
def like_album(request, id):
    if request.htmx:
        profile = request.user.profile_set.first()
        added=False
        
        # CHECK IF THERE'S A REGISTER
        liked_albums = Liked_albums.objects.filter(profile=profile)
        if liked_albums.exists():
            albums = liked_albums.first().albums
            
            # CHECK IF ADD OR REMOVE LIKE
            if albums.filter(id=id).exists():
                albums.remove(id)
            else:
                albums.add(id)
                added=True
            
        else:
            # CREATE REGISTER
            liked_album = Liked_albums(profile=profile)
            liked_album.save()
            
            # ADD LIKED ALBUM
            liked_albums = Liked_albums.objects.filter(profile=profile).first()
            liked_albums.albums.add(id)
            added=True
            
        album = Album.objects.filter(id=id).first()
        return render(request, 'list.html#albumElement', {"album": album, "added":added})
    
@login_required
def like_list(request, id):
    if request.htmx:
        profile = request.user.profile_set.first()
        added=False
        
        # CHECK IF THERE'S A REGISTER
        liked_list = Liked_lists.objects.filter(profile=profile)
        if liked_list.exists():
            lists = liked_list.first().lists
            
            # CHECK IF ADD OR REMOVE LIKE
            if lists.filter(id=id).exists():
                lists.remove(id)
            else:
                lists.add(id)
                added=True
            
        else:
            # CREATE REGISTER
            liked_list = Liked_lists(profile=profile)
            liked_list.save()
            
            # ADD LIKED ALBUM
            liked_list = Liked_lists.objects.filter(profile=profile).first()
            liked_list.lists.add(id)
            added=True
            
        list_object = List.objects.filter(id=id).first()
        return render(request, 'list.html#listLikeElement', {"list": list_object, "added":added})

@login_required
def follow_artist(request, id):
    if request.htmx:
        profile = request.user.profile_set.first()
        added=False
        
        # CHECK IF THERE'S A REGISTER
        follow_artist = Followed_artists.objects.filter(profile=profile)
        if follow_artist.exists():
            artists = follow_artist.first().artists
            
            # CHECK IF ADD OR REMOVE LIKE
            if artists.filter(id=id).exists():
                artists.remove(id)
            else:
                artists.add(id)
                added=True
            
        else:
            # CREATE REGISTER
            follow_artist = Followed_artists(profile=profile)
            follow_artist.save()
            
            # ADD LIKED ALBUM
            follow_artist = Followed_artists.objects.filter(profile=profile).first()
            follow_artist.artists.add(id)
            added=True
            
        artist = Artist.objects.filter(id=id).first()
        return render(request, 'list.html#artistElement', {"artist": artist, "added":added})

@login_required
def liked_musics(request):
    profile = request.user.profile_set.first()
    context = {}    
    
    musics = Liked_musics.objects.filter(profile=profile).first().musics.order_by('-lm_musics__created_at').all()
    context.update({
        'musics': musics,
        'profile': profile,
        'nameList': 'liked_musics'
    })
    
    if request.htmx:
        return render(request, 'list.html#list', context)
    else:
        context.update(get_library(request))
        return render(request, 'list.html', context)

def view_list(request, id):
    context = {}
    try:
        list_object = get_object_or_404(List, id=id)
        musics = list_object.musics.order_by('l_musics__created_at').all()
        context.update({
            'list': list_object,
            'musics': musics,
            'nameList': list_object.name,
            'profile': list_object.profile,
        })
        
    except Http404:
        if request.htmx:
            return render(request, '404.html#error_404')
        else:
            if request.user.is_authenticated:
                return render(request, '404.html', get_library(request), status=404)
            else:
                return render(request, '404.html', status=404)
            
    if request.htmx:
        if request.user.is_authenticated:
            profile = request.user.profile_set.first()
            like_exist = Liked_lists.objects.filter(profile=profile, lists=list_object).exists()
            context.update({ 'liked': like_exist})
            
        return render(request, 'list.html#list', context)
    
    else:
        if request.user.is_authenticated:
            profile = request.user.profile_set.first()
            like_exist = Liked_lists.objects.filter(profile=profile, lists=list_object).exists()
            context.update({ 'liked': like_exist})
            context.update(get_library(request))
        else:
            context.update({ 'login': FormLogin})
            
        return render(request, 'list.html', context)

@login_required
def view_mylist(request, name):
    context = {}
    try:
        profile = request.user.profile_set.first()
        list_object = get_object_or_404(List, name=name, profile=profile)
        musics = list_object.musics.order_by('l_musics__created_at').all()
        context.update({
            'list': list_object,
            'musics': musics, 
            'nameList': name, 
            'profile': profile
        })
            
    except Http404:
        if request.htmx:
            return render(request, '404.html#error_404')
        else:
            return render(request, '404.html', get_library(request), status=404)
    
    if request.htmx:
        return render(request, 'list.html#list', context)
       
    else:
        context.update(get_library(request))
        return render(request, 'list.html', context)

@login_required
def new_list(request):
    if request.method == 'POST':
        data = request.POST['name']
        if len(data) > 0:     
            profile = request.user.profile_set.first()
            list_object = List.objects.filter(profile=profile, name=data)
            exists = False
            
            if len(data) > 40:
                return render(request, 'modal.html#modalNewList', { 'largeName': True})
            
            if list_object.exists():
                exists = True
            else:
                new_list = List(name=data, profile=profile)
                new_list.save()
            
            if exists:
                return render(request, 'modal.html#modalNewList', { 'exists': exists})
            else:
                response = HttpResponse()
                response['HX-Refresh'] = 'true'
                return response
        else:
            return render(request, 'modal.html#modalNewList', { 'isEmpty': True})
        
@login_required
def edit_list(request, id_list):
    if request.method == 'POST':
        data = request.POST['name']
        
        # CHECK IF INPUT IS EMPTY
        if len(data) > 0:
            list_object = List.objects.filter(id=id_list).first()
            
            # MAXIMUM LENGHT
            if len(data) > 40:
                context = {
                    "largeName": True,
                    "list": list_object
                }
                return render(request, 'modal.html#editList', context)
            
            # CHECK IF NAME ALREADY EXIST
            if list_object.name == data:
                context = {
                    "exists": True,
                    "list": list_object
                }
                return render(request, 'modal.html#editList', context)
            else:
                list_object.name = data
                list_object.save()
                
                response = HttpResponse()
                response['HX-Redirect'] = '/my_lists/' + data
                return response
                
        else:
            list_object = List.objects.filter(id=id_list).first()
            context = {
                "isEmpty": True,
                "list": list_object
            }
            return render(request, 'modal.html#editList', context)
            
    
@login_required    
def delete_list(request, name):
    profile = request.user.profile_set.first()
    List.objects.filter(profile=profile, name=name).delete()
    
    response = HttpResponse('')
    response['HX-Redirect'] = '/'
    return response

@login_required
def add_to_list(request, id_music, id_list):
    if request.htmx:
        profile = request.user.profile_set.first()
        added = False
        
        music = Music.objects.filter(id=id_music).first()
        list_object = List.objects.filter(profile=profile, id=id_list).first()
        
        # CHECK IF THERE'S A REGISTER
        music_exists = List.objects.filter(id=id_list, musics=music).exists()
        if music_exists:
            list_object.musics.remove(id_music)
        else:
            list_object.musics.add(id_music)
            added = True
            
        # CHECK URL
        likedMusics = str(request.META.get("HTTP_REFERER")).find('liked_musics')
        isListView = False
        if likedMusics < 0:           
            # CHECK MYLIST
            isListView = str(request.META.get("HTTP_REFERER")).find('my_lists')
            isListView = True if isListView > 0 else False
            
            # CHECK NAME LIST
            isListView = str(request.META.get("HTTP_REFERER")).find(list_object.name)
            isListView = True if isListView > 0 else False
            
        musics = list_object.musics.order_by('l_musics__created_at').all() if isListView else None
        
        context = {
            'id_music': id_music,
            'nameList': list_object.name,
            'list': list_object,
            'musics': musics,
            'added': added,
            'isListView': isListView,
            'profile': request.user.profile_set.first()
        }
        return render(request, 'list.html#listElement', context)

# MANAGEMENT
@login_required(login_url="/login")
def management(request):
    artist = Artist.objects.filter(user=request.user.id).first()
    if artist:
        musics = Music.objects.filter(artist=artist.id)
        form = FormMusics(user=request.user, initial=True)
        return render(
            request, "pages/admin.html", {"musics": musics, "FormMusics": form}
        )
    else:
        return render(request, "pages/admin.html#not_artist")


# ALBUMS
@login_required()
def management_albums(request):
    if request.method == "POST":
        form = FormAlbums(request.POST, request.FILES)
        if form.is_valid():
            album = form.save(commit=False)
            artist = Artist.objects.filter(user=request.user.id).first()
            album.artist = artist
            album.save()

            albums = Album.objects.filter(artist=artist.id)
            return render(
                request,
                "pages/admin.html#albums",
                {"albums": albums, "FormAlbums": FormAlbums},
            )
    else:
        artist = Artist.objects.filter(user=request.user.id).first()
        albums = Album.objects.filter(artist=artist.id)
        return render(request, "pages/admin.html#albums",{"albums": albums, "FormAlbums": FormAlbums})


@login_required()
def management_album(request, id):
    if request.method == "POST":
        album = Album.objects.filter(id=id).first()
        form = FormAlbums(request.POST, request.FILES, instance=album)
        if form.is_valid():
            form.save()

            artist = Artist.objects.filter(user=request.user.id).first()
            albums = Album.objects.filter(artist=artist)
            return render(request,"pages/admin.html#albums", {
                "albums": albums, 
                "FormAlbums": FormAlbums})

    if request.method == "DELETE":
        Album.objects.filter(id=id).delete()

        artist = Artist.objects.filter(user=request.user.id).first()
        albums = Album.objects.filter(artist=artist.id)
        return render( request,"pages/admin.html#albums", {
            "albums": albums, 
            "FormAlbums": FormAlbums})


@login_required()
def management_album_edit(request, id):
    album = Album.objects.filter(id=id).first()
    form = FormAlbums(instance=album)
    context = {"FormAlbums": form, "id": id, "album": album}
    return render(request, "pages/admin.html#editAlbum", context)


@login_required()
def management_album_new(request):
    if request.method == "GET":
        return render(request, "pages/admin.html#newAlbum", {"FormAlbums": FormAlbums})


# MUSICS
@login_required()
def management_musics(request):
    if request.method == "POST":
        form = FormMusics(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            music = form.save(commit=False)
            artist = Artist.objects.filter(user=request.user.id).first()
            music.artist = artist
            music.save()

            # ADD GENRE 
            genres = form.cleaned_data['genre']
            music.genre_set.clear()
            for genre in genres:
                music.genre_set.add(genre.id)

            musics = Music.objects.filter(artist=artist)
            form = FormMusics(user=request.user)
            return render(request, "pages/admin.html#musics", {"FormMusics": form, "musics": musics})
        else:
            artist = Artist.objects.filter(user=request.user.id).first()
            musics = Music.objects.filter(artist=artist)
            return render(request, "pages/admin.html#musics", {"FormMusics": form, "musics": musics})
    else: 
        artist = Artist.objects.filter(user=request.user.id).first()
        musics = Music.objects.filter(artist=artist)
        form = FormMusics(user=request.user, initial=True)
        return render(request, "pages/admin.html#musics", {"FormMusics": form, "musics": musics})


@login_required()
def management_music(request, id):
    if request.method == "POST":
        music = Music.objects.filter(id=id).first()
        current_album = music.album.name
        
        form = FormMusics(request.POST, request.FILES, instance=music, user=request.user)
        if form.is_valid():
            # VERIFY TO DELETE IMG
            new_album = form.cleaned_data['album'].name
            if new_album != 'Ninguno' and current_album == 'Ninguno':
                music.img = None
                music.save()
                
            form.save()
            
            # ADD GENRE 
            genres = form.cleaned_data['genre'] 
            music.genre_set.clear()
            for genre in genres:
                music.genre_set.add(genre.id)

            # RESPONSE
            artist = Artist.objects.filter(user=request.user.id).first()
            musics = Music.objects.filter(artist=artist)
            form = FormMusics(user=request.user)
            return render(request, "pages/admin.html#musics", {"FormMusics": form, "musics": musics})
        
    elif request.method == 'DELETE':
        music = Music.objects.filter(id=id)
        music.delete()

        artist = Artist.objects.filter(user=request.user.id).first()
        musics = Music.objects.filter(artist=artist)
        form = FormMusics(user=request.user)
        return render(request, "pages/admin.html#musics", {"FormMusics": form, "musics": musics})
    
    else:
        music = Music.objects.filter(id=id).first()
        return render(request, "modal.html#modalMusic", { 'music': music })



@login_required()
def management_music_new(request):
    form = FormMusics(user=request.user, initial=True)
    return render(request, "pages/admin.html#newMusic", {"FormMusics": form})

@login_required()
def management_music_edit(request, id):
    music = Music.objects.filter(id=id).first()
    form = FormMusics(initial={"genre": music.genre_set.all()}, instance=music, user=request.user)
    context = {
        "FormMusics": form, 
        "music": music
    }
    return render(request, "pages/admin.html#editMusic", context)
