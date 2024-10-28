from .models import ArtistProfile, Album, ListenerProfile, Playlist, Comment, Order, LikedPlaylist
from .models import Follow
from .models import GenreInteraction
from django.contrib import admin
from .models import Brano
from .models import Merchandise
from .models import Genre

admin.site.register(ArtistProfile)
admin.site.register(ListenerProfile)
admin.site.register(Album)
admin.site.register(Brano)
admin.site.register(Merchandise)
admin.site.register(Genre)
admin.site.register(Follow)
admin.site.register(GenreInteraction)
admin.site.register(Playlist)
admin.site.register(Comment)
admin.site.register(Order)
admin.site.register(LikedPlaylist)
