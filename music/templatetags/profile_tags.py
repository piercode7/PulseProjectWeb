# profile_tags.py in music/templatetags
from django import template
from music.models import ArtistProfile, ListenerProfile

register = template.Library()

@register.simple_tag(takes_context=True)
def user_profile_url(context):
    request = context['request']
    user = request.user
    if user.is_authenticated:
        if ArtistProfile.objects.filter(user=user).exists():
            return 'private_artist_profile'
        elif ListenerProfile.objects.filter(user=user).exists():
            return 'listener_profile'
    return ''
