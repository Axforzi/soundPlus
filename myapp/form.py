from typing import Any
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from .models import *

class FormLogin(forms.Form):
    username = forms.CharField(label="Correo electrónico o nombre de usuario", 
                            label_suffix="",
                            max_length=100, 
                            widget=forms.TextInput(
                                attrs={ "placeholder": "Correo electrónico o nombre de usuario" }
                            ))
    password = forms.CharField(
        label="Contraseña",
        label_suffix="",
        widget=forms.PasswordInput(attrs={"placeholder": "Contraseña"}))
    
class FormSignup(UserCreationForm):
    first_name = forms.CharField(max_length=100,
                                 label="Nombre",
                                 label_suffix="",
                                 widget=forms.TextInput(attrs={"placeholder": "Nombre", 'autofocus': 'True'}))
    
    last_name = forms.CharField(max_length=100,
                                label="Apellido",
                                label_suffix="",
                                widget=forms.TextInput(attrs={"placeholder": "Apellido"}))
    
    email = forms.CharField(label='Dirección de correo electrónico',
                            label_suffix='',
                            widget=forms.EmailInput(attrs={'placeholder': 'Correo electrónico'}))
    
    username = forms.CharField(max_length=50,
                               label='Usuario',
                               label_suffix='',
                               widget=forms.TextInput(attrs={'placeholder': 'Usuario'}))
    
    password1 = forms.CharField(label='Contraseña',
                                label_suffix='',
                                widget=forms.PasswordInput(attrs={ 'placeholder': 'Contraseña' }),
                                help_text=None)
    
    password2 = forms.CharField(label='Contraseña (confirmación)',
                                label_suffix='',
                                widget=forms.PasswordInput(attrs={ 'placeholder': 'Vuelve a escribir la contraseña' }),
                                help_text=None)
    
    
    
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'username', 'password1', 'password2']

class FormAlbums(forms.ModelForm):
    ALBUM_TYPES = (
        ('0', 'Album'),
        ('1', 'EP')
    )
    attrs = {
        'hx-on:click': "htmx.toggleClass('.select.album-type', 'select-show'); htmx.find('.album-type span').innerHTML = this.parentNode.textContent"
    }
    
    name = forms.CharField(label='',
                           max_length=100, 
                           widget=forms.TextInput(attrs={'placeholder': 'Nombre del album'}))
    img = forms.ImageField(label='Portada del album', widget=forms.FileInput(attrs={'onchange': 'previewImg(event)'}))
    album_type = forms.ChoiceField(label='Tipo de album', required=False, choices=ALBUM_TYPES,widget=forms.RadioSelect(attrs=attrs))
    
    def clean_album_type(self):
        album_type = self.cleaned_data['album_type']
        
        if album_type != '':
            album_type = int(self.cleaned_data['album_type'])
        else:
            album_type = 0
            
        return album_type

    class Meta():
        model = Album
        fields = ['name', 'album_type', 'img']

class FormMusics(forms.ModelForm):
    name = forms.CharField(label='',
                           label_suffix='',
                           max_length=100,
                           widget=forms.TextInput(attrs={'placeholder': 'Nombre de la canción'}))
    song = forms.FileField(label='Canción', label_suffix='',widget=forms.FileInput())
    img = forms.ImageField(label='Portada de la canción', label_suffix='', widget=forms.FileInput(attrs={'onchange': 'previewImg(event)'}))

    # CONFIG SELECT
    attrs = {
        'hx-on:click': "htmx.toggleClass('.select.album', 'select-show'); htmx.find('.album span').innerHTML = this.parentNode.textContent",
        'onchange': 'onSelectAlbum(event)'
    }
    album = forms.ModelChoiceField(queryset=Album.objects.none(),label_suffix='', widget=forms.RadioSelect(attrs=attrs))
    genre = forms.ModelMultipleChoiceField(label='Generos', label_suffix='', required=False,queryset=Genre.objects.all(), widget=forms.CheckboxSelectMultiple())

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user')
        initial = kwargs.pop('initial', None)
        artist = kwargs.pop('artist', None)
        self.artist = artist if artist is not None else Artist.objects.filter(user=user.id).first()
        
        super().__init__(*args, **kwargs)
        
        queryset = Album.objects.filter(name='Ninguno') | Album.objects.filter(artist=self.artist)
        self.fields['album'].queryset = queryset
        if (initial is not None) and queryset.exists():
            self.fields['album'].initial = queryset[0]
        
        # VALIDATE ALBUM
        if self.instance.album != None:
            self.fields['img'].required = False if self.instance.album.name != 'Ninguno' else True
            
        if self.data.get('album', None) != None:
            self.fields['img'].required = False if self.data.get('album', None) != 1 else True
            
        # VALIDATE GENRES
        if type(initial) == dict:
            if initial['genre'] is not None:
                self.fields['genre'].initial = initial['genre']

    class Meta:
        model = Music
        fields = ['name', 'genre', 'album', 'song', 'img']

class FormEditProfile(forms.ModelForm):
    profileImg = forms.ImageField(label='', required=False, widget=forms.FileInput(attrs={'onchange': 'imgProfile(event)'}))
    coverImg = forms.ImageField(label='', required=False, widget=forms.FileInput())
    name = forms.CharField(label='', max_length=100, required=True)

    class Meta:
        model = Profile
        fields = ['profileImg', 'coverImg', 'name']


class FormEditArtistAccount(forms.ModelForm):
    profileImg = forms.ImageField(label='', required=False, widget=forms.FileInput(attrs={'onchange': 'imgArtistPreview(event)'}))
    coverImg = forms.ImageField(label='', required=False, widget=forms.FileInput(attrs={'onchange': 'backgroundArtistPreview(event)'}))
    name = forms.CharField(label='', max_length=100, required=False, widget=forms.TextInput(attrs={'placeholder': 'Nombre de artista', 'onkeyup': 'previewTitle(event)'}))

    def clean_name(self):
        name = self.cleaned_data['name']
        artist = Artist.objects.filter(name=name).first()
        artist = artist.name if artist is not None else ''
        if name == '':
            raise ValidationError('No se ha ingresado un nombre de artista', code='no_artist_name')
        if name == artist:
            raise ValidationError('Este nombre de artista ya esta siendo utilizado', code='artist_name_used')
        
        return name

    class Meta:
        model = Artist
        fields = ['profileImg', 'coverImg', 'name']
        
class FormNewList(forms.ModelForm):
    name = forms.CharField(label='', max_length=100, required=True, widget=forms.TextInput(attrs={'placeholder': 'Nombre de la lista'}))
    
    class Meta:
        model = List
        fields = ['name']