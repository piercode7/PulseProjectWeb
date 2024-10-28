
from django.urls import path

from . import views_profile, views_account, views_mystuff, views_editstuff, views_explore, views_transaction, \
    views_social, views_addstuff, views_utils

urlpatterns = [

# accpunt
    path('restore_profile/', views_account.restore_profile, name='forgot_user_password'),
    path('recover_password/', views_account.recover_password, name='recover_password'),
    path('confirm_password_change/<uidb64>/<token>/', views_account.confirm_password_change, name='confirm_password_change'),
    path('recover_username/', views_account.recover_username, name='recover_username'),
    path('confirm_username_change/<uidb64>/<token>/', views_account.confirm_username_change, name='confirm_username_change'),
    # modifiche utente
    path('<str:username>/private/account/change_email/', views_account.start_email_change, name='start_email_change'),
    path('confirm_email_change/<uidb64>/<token>/', views_account.confirm_email_change, name='confirm_email_change'),
    path('account/delete/', views_account.request_account_deletion, name='request_account_deletion'),
    path('account/delete/confirm/<uidb64>/<token>/', views_account.confirm_account_deletion,
         name='confirm_account_deletion'),


    path('my_profile/', views_profile.my_profile, name='my_profile'),
    path('my_page/', views_profile.my_page, name='my_page'),
    path('choose_profile_type/', views_profile.choose_profile_type, name='choose_profile_type'),
    path('create_artist_profile/', views_profile.create_artist_profile, name='create_artist_profile'),
    path('create_listener_profile/', views_profile.create_listener_profile, name='create_listener_profile'),
    path('profile/<str:username>/', views_profile.profile_redirect, name='profile_redirect'),
    path('profile/<str:username>/interactions/reset/', views_editstuff.reset_interactions, name='reset_interactions'),

    # ARTIST PRIVATO
    path('artist/<str:username>/private/', views_profile.private_artist_profile, name='private_artist_profile'),
    path('artist/<str:username>/private/albums/', views_mystuff.my_albums, name='my_albums'),
    path('artist/<str:username>/private/orders/', views_mystuff.artist_orders, name='artist_orders'),
    path('artist/<str:username>/private/albums/<int:album_id>/toggle-published/', views_profile.toggle_album_published, name='toggle_album_published'),
    path('artist/<str:username>/private/albums/<int:album_id>/add_brano_to_album/', views_addstuff.add_brano_to_album, name='add_brano_to_album'),
    path('artist/<str:username>/private/albums/<int:album_id>/add_multiple_brani/', views_addstuff.add_multiple_brani,name='add_multiple_brani'),
    path('artist/<str:username>/private/albums/<int:album_id>/update_cover/', views_editstuff.update_album_cover, name='update_album_cover'),
    path('artist/<str:username>/private/albums/<int:album_id>/show_album_cover/', views_utils.show_album_cover, name='show_album_cover'),
    path('artist/<str:username>/private/albums/<int:album_id>/delete/', views_editstuff.delete_album, name='delete_album'),
    path('artist/<str:username>/private/albums/<int:album_id>/edit/', views_editstuff.edit_album, name='edit_album'),
    path('artist/<str:username>/private/album/<int:album_id>/brano/<int:brano_id>/edit/', views_editstuff.edit_brano, name='edit_brano'),
    path('artist/<str:username>/private/album/<int:album_id>/brano/<int:brano_id>/delete/', views_editstuff.delete_song,name='delete_song'),
    path('artist/<str:username>/private/registeralbum/', views_addstuff.register_album, name='register_album'),
    path('artist/<str:username>/album/<int:album_id>/viewalbum', views_utils.view_album, name='view_album'),
    path('artist/<str:username>/private/merchandise/', views_mystuff.my_merch, name='my_merch'),
    path('artist/<str:username>/private/merchandise/add/', views_addstuff.create_merchandise, name='create_merch'),
    path('artist/<str:username>/private/merchandise/<int:merch_id>/edit/', views_editstuff.edit_merch, name='edit_merch'),



    # ARTIST PUBBLICO
    path('artist/<str:username>/albums', views_profile.public_artist_profile, name='public_artist_profile'),
    path('artist/<str:username>/merchandise/', views_profile.public_artist_merch, name='public_artist_merch'),
    path('listener/<str:username>/artists/', views_profile.public_listener_artists, name='public_listener_artists'),
    path('listener/<str:username>/playlists/', views_profile.public_listener_playlists, name='public_listener_playlists'),

    path('listener/<str:username>/private', views_profile.private_listener_profile, name='private_listener_profile'),
    path('listener/<str:username>/private/account', views_account.my_account, name='my_account'),
    path('listener/<str:username>/private/shopping/', views_mystuff.my_shopping, name='my_shopping'),
    path('listener/<str:username>/following/', views_social.following_list, name='following_list'),
    path('listener/<str:username>/private/account/send_test_email/', views_account.send_test_email, name='send_test_email'),
    path('artist/<str:username>/merchandise/<int:merch_id>/buy/', views_transaction.buy_merchandise,
         name='buy_merchandise'),
    path('paypal/return/', views_transaction.paypal_return, name='paypal_return'),
    path('paypal/cancel/', views_transaction.paypal_cancel, name='paypal_cancel'),

# my listener stuff
    path('listener/<str:username>/private/playlists/', views_mystuff.my_playlists, name='my_playlists'),
    path('listener/<str:username>/private/comments/', views_mystuff.my_comments, name='my_comments'),
    path('<str:username>/profile/interactions/', views_mystuff.my_interactions, name='my_interactions'),
    path('listener/<str:username>/playlists/delete/<int:playlist_id>/', views_editstuff.delete_playlist, name='delete_playlist'),
    path('listener/<str:username>/playlist/<int:playlist_id>/', views_utils.view_playlist, name='view_playlist'),
    path('listener/<str:username>/playlist/<int:playlist_id>/delete-track/<int:track_id>/',
         views_editstuff.delete_track_from_playlist, name='delete_track_from_playlist'),
    path('listener/<str:username>/private/registerplaylist/', views_addstuff.register_playlist, name='register_playlist'),
    path('listener/<str:username>/choose_playlist/<int:track_id>/', views_utils.choose_playlist, name='choose_playlist'),
    path('listener/<str:username>/add_to_playlist/<int:playlist_id>/<int:track_id>/', views_addstuff.add_to_playlist,
         name='add_to_playlist'),
    path('<str:username>/update_interactions/', views_utils.update_interactions, name='update_interactions'),
    path('increment_play_count/', views_utils.increment_play_count, name='increment_play_count'),






# explore
    path('search/', views_explore.search_profiles, name='search_profiles'),
    path('search/artist_results/<str:search_term>/', views_explore.artist_results, name='artist_results'),
    path('search/listener_results/<str:search_term>/', views_explore.listener_results, name='listener_results'),
    path('search/albums/<str:search_term>/', views_explore.album_results, name='album_results'),
    path('search/songs/<str:search_term>/', views_explore.song_results, name='song_results'),
    path('explore/', views_explore.explore_view, name='explore'),
    path('genrelist/', views_explore.genre_list, name='genre_list'),
    path('genrelist/<int:genre_id>/', views_explore.genre_area, name='genre_area'),



# social
    path('<str:username>/profile/followers/', views_mystuff.followers_list, name='followers_list'),
    path('<str:username>/follow/', views_social.follow_artist, name='follow_artist'),
    path('<str:username>/unfollow/', views_social.unfollow_artist, name='unfollow_artist'),
    path('playlist/link/<int:playlist_id>/', views_social.link_playlist, name='link_playlist'),
    path('playlist/unlink/<int:playlist_id>/', views_social.unlink_playlist, name='unlink_playlist'),
    path('notifications/', views_social.notification_center, name='notification_center'),
    path('notifications/read/<int:notification_id>/', views_social.mark_notification_as_read,
         name='mark_notification_as_read'),
    path('notifications/delete_all/', views_editstuff.delete_all_notifications, name='delete_all_notifications'),
    path('artist/<str:username>/discussion/', views_social.artist_discussion, name='artist_discussion'),
    path('comment/delete/<int:comment_id>/', views_editstuff.delete_comment, name='delete_comment'),


]

