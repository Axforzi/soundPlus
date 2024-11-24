from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    
    # LOGIN 
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('signup/', views.signup, name='signup'),
    
    path('profile/<id>', views.profile_view, name='profile_view'),
    path('my_profile/', views.myprofile_view, name='my_profile_view'),
    path('profile-save/', views.profile_save, name='profile_save'),

    path('artist-account/', views.artist_account_view, name='artist_account'),
    path('create-artist/', views.create_artist, name='create_artist'),
    path('artist-account-save/', views.artist_account_save, name='artist_account_save'),

    # VIEW_PAGES 
    path('artist/<artist_name>', views.artist_view, name='artist_view'),
    path('artist/<artist_name>/album/<album_name>', views.album_view, name='album_view'),
    path('artist/<artist_name>/single/<single_name>', views.single_view, name='single_view'),
    path('artist/<artist_name>/discography', views.discography_view, name='discography_view'),
    path('popular/<section>', views.section_view, name="section_view"),
    path('my_lists/<name>', views.view_mylist, name='view_mylist'),
    path('list/<id>', views.view_list, name='view_list'),
    path('liked_musics/', views.liked_musics, name='liked_musics'),
    
    # SEARCH
    path('search/', views.search, name='search'),
    path('search-artists/', views.search_artist, name='search_artist'),

    #PLAY MUSIC
    path('play/artist/<artist_name>', views.play_artist, name='play_artist'),
    path('play/album/<id>', views.play_album, name='play_album'),
    path('play/music/<id>', views.play_music, name='play_music'),
    path('play/list/<id>', views.play_list, name='play_list'),
    path('play/liked_musics', views.play_liked_musics, name='play_liked_musics'),
    path('play/liked_musics/<id>', views.play_liked_music, name='play_liked_music'),
    path('play/music_album/<id>', views.play_music_on_album, name='play_music_album'),
    path('play/list/<id_list>/<id_music>', views.play_music_on_list, name='play_music_list'),
    path('play/add_queue/<id>', views.add_queue, name='add_queue'),
    path('serve_music/<id_music>', views.serve_music, name='serve_music'),
    
    #LIKE AND FOLLOWS
    path('like_music/<id>', views.like_music, name='like_music'),
    path('like_album/<id>', views.like_album, name='like_album'),
    path('like_list/<id>', views.like_list, name='like_list'),
    path('follow_artist/<id>', views.follow_artist, name='follow_artist'),
    
    #LIST
    path('new_list/', views.new_list, name='new_list'),
    path('edit_list/<id_list>', views.edit_list, name='edit_list'),
    path('add_to_list/<id_list>/music/<id_music>', views.add_to_list, name='add_to_list'),
    path('delete_list/<name>', views.delete_list, name='delete_list'),

    #MANAGEMENT
    path('management/', views.management, name='management'),
    
    #ALBUMS
    path('management/albums', views.management_albums, name='management_albums'),
    path('management/albums/<id>', views.management_album, name='management_album'),
    
    path('management/albums/<id>/edit', views.management_album_edit, name='management_album_edit'),
    path('management/new-album', views.management_album_new, name='management_album_new'),

    #MUSICS
    path('management/musics', views.management_musics, name='management_musics'),
    path('management/musics/<id>', views.management_music, name='management_music'),

    path('management/musics/<id>/edit', views.management_music_edit, name='management_music_edit'),
    path('management/new-music', views.management_music_new, name='management_music_new')
]