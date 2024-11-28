from django import template
from myapp.models import List, Artist, Followed_artists, Liked_musics, Liked_albums
import os

register = template.Library()

@register.filter
def imgUrl(img):
    return f"https://{os.getenv('SUPABASE_PROJECT_URL')}/storage/v1/object/public/{os.getenv('SUPABASE_BUCKET_NAME')}/{img}"

@register.filter
def liked_user(music, user):
    profile = user.profile_set.first()
    liked = music.liked_musics_set.filter(profile=profile).exists()
    return liked

@register.filter
def check_list(music, list_object):
    in_list = List.objects.filter(id=list_object.id, musics=music).exists()
    return in_list

@register.filter
def musics_list_count(list_id):
    musics_count = List.objects.filter(id=list_id).first().musics.count()
    return musics_count

@register.filter
def followers_count(artist):
    followers = Followed_artists.objects.filter(artists=artist).count()
    return followers

@register.filter
def music_likes(music):
    likes = Liked_musics.objects.filter(musics=music).count()
    return likes

@register.filter
def album_likes(album):
    likes = Liked_albums.objects.filter(albums=album).count()
    return likes

@register.filter
def artist_by_album(album_id):
    artist = Artist.objects.filter(album=album_id).first()
    return artist.name