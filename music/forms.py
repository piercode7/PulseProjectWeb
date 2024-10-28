from django import forms
from django.contrib.auth.models import User
from .models import ArtistProfile, ListenerProfile, Album

# forms.py in music
from django import forms


class ProfileCreationForm(forms.Form):
    PROFILE_CHOICES = (
        ('artist', 'Artista'),
        ('listener', 'Ascoltatore'),
    )
    profile_type = forms.ChoiceField(choices=PROFILE_CHOICES, widget=forms.RadioSelect)


from django import forms
from django.contrib.auth.models import User
from music.models import ArtistProfile


class ArtistRegistrationForm(forms.ModelForm):
    username = forms.CharField(max_length=150)
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = ArtistProfile
        fields = ['name', 'bio']

    def save(self, commit=True):
        user = User.objects.create_user(
            username=self.cleaned_data['username'],
            email=self.cleaned_data['email'],
            password=self.cleaned_data['password']
        )
        artist_profile = super().save(commit=False)
        artist_profile.user = user
        if commit:
            artist_profile.save()
        return artist_profile


# music/forms.py


from .models import ArtistProfile, ListenerProfile

# forms.py in music
from django import forms
from .models import ArtistProfile


class ArtistProfileForm(forms.ModelForm):
    class Meta:
        model = ArtistProfile
        fields = ['name', 'bio', 'photo_image']


class ListenerProfileForm(forms.ModelForm):
    class Meta:
        model = ListenerProfile
        fields = ['name', 'bio', 'photo_image', 'listening_mode']


class AlbumForm(forms.ModelForm):
    class Meta:
        model = Album
        fields = ['title', 'genre', 'release_date']


from django import forms
from .models import Playlist
from datetime import date


class PlaylistForm(forms.ModelForm):
    class Meta:
        model = Playlist
        fields = ['title', 'release_date']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.instance.pk:
            self.fields['release_date'].initial = date.today()


from django import forms
from .models import Brano
from django import forms
from .models import Brano
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, TIT2, TRCK
from datetime import timedelta

class BranoForm(forms.ModelForm):
    class Meta:
        model = Brano
        fields = ['title', 'side', 'track_index', 'duration', 'mp3_file']  # Removed genre

    def __init__(self, *args, **kwargs):
        album = kwargs.pop('album', None)
        super(BranoForm, self).__init__(*args, **kwargs)
        self.album = album  # Save the album reference for use in save()

    def save(self, commit=True):
        instance = super(BranoForm, self).save(commit=False)
        instance.artist = self.album.artist
        instance.album = self.album
        instance.genre = self.album.genre  # Set genre from album

        mp3_file = self.cleaned_data.get('mp3_file')

        if mp3_file:
            # Usa mutagen per estrarre i metadati MP3
            try:
                audio = MP3(mp3_file)
                id3_tags = audio.tags

                # Se il titolo non è stato fornito dall'utente, prova a estrarlo dai tag
                if not instance.title and id3_tags:
                    instance.title = id3_tags.get(TIT2, 'Unknown Title').text[0]

                # Estrazione della durata dal file MP3 (convertito in timedelta)
                instance.duration = timedelta(seconds=int(audio.info.length))

                # Estrazione dell'indice traccia, se disponibile nei tag
                if not instance.track_index and id3_tags:
                    track_info = id3_tags.get(TRCK)
                    if track_info:
                        instance.track_index = int(track_info.text[0].split('/')[0])

            except Exception as e:
                # In caso di errore con mutagen, puoi gestire l'errore come preferisci
                # Ad esempio, potresti loggare l'errore o impostare dei valori predefiniti
                print(f"Errore durante l'estrazione dei metadati: {e}")

        if commit:
            instance.save()
            self.save_m2m()

        return instance


from django import forms
from .models import Album


class AlbumCoverForm(forms.ModelForm):
    class Meta:
        model = Album
        fields = ['cover_image']


from django import forms
from .models import Album, Genre


class AlbumRegistrationForm(forms.ModelForm):
    # Aggiungi un campo genre che elenca i generi dal modello Genre
    genre = forms.ModelChoiceField(queryset=Genre.objects.all(), empty_label="Choose a genre")

    class Meta:
        model = Album
        fields = ['title', 'genre', 'release_date']

    def __init__(self, *args, **kwargs):
        super(AlbumRegistrationForm, self).__init__(*args, **kwargs)
        # Puoi ordinare o filtrare i generi qui se necessario
        self.fields['genre'].queryset = Genre.objects.all().order_by('name')


class ArtistSearchForm(forms.Form):
    search_term = forms.CharField(label='Cerca Artista', max_length=100)


from django import forms


class ListenerSearchForm(forms.Form):
    search_term = forms.CharField(label='Cerca Ascoltatore', max_length=100)


from django import forms


class SearchForm(forms.Form):
    search_term = forms.CharField(label='Search', max_length=100)


from django import forms
from .models import Merchandise


class MerchandiseForm(forms.ModelForm):
    class Meta:
        model = Merchandise
        fields = ['name', 'description', 'price', 'image', 'stock_quantity']
        labels = {
            'name': 'Name',
            'description': 'Description',
            'price': 'Price',
            'image': 'Image',
            'stock_quantity': 'Quantity'
        }
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control'}),
            'price': forms.NumberInput(attrs={'class': 'form-control'}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'stock_quantity': forms.NumberInput(attrs={'class': 'form-control'}),
        }

    def clean_price(self):
        price = self.cleaned_data.get('price')
        if price <= 0:
            raise forms.ValidationError("Insert a price > 0.")
        return price

    def clean_stock_quantity(self):
        stock_quantity = self.cleaned_data.get('stock_quantity')
        if stock_quantity < 0:
            raise forms.ValidationError("The quantity must be > 0.")
        return stock_quantity


from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import PasswordChangeForm


class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['email']


class CustomPasswordChangeForm(PasswordChangeForm):
    class Meta:
        model = User
        fields = ['old_password', 'new_password1', 'new_password2']


from django import forms
from .models import Comment


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['album', 'content', 'parent']
        widgets = {
            'album': forms.Select(attrs={'class': 'form-control'}),
            'content': forms.Textarea(
                attrs={'rows': 4, 'class': 'form-control', 'placeholder': 'Write your comment here...'}),
            'parent': forms.HiddenInput(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['album'].required = False
        self.fields['album'].label = "Album (Optional)"


from django import forms


class PurchaseForm(forms.Form):
    quantity = forms.IntegerField(
        min_value=1,
        required=True,
        error_messages={'min_value': 'Invalid quantity. Please enter a positive number.'}
    )
    shipping_address = forms.CharField(max_length=255, required=True)
    shipping_city = forms.CharField(max_length=100, required=True)
    shipping_zip = forms.RegexField(
        regex=r'^\d{5}$',
        error_messages={'invalid': "Enter a valid ZIP code."},
        required=True
    )
    shipping_phone = forms.RegexField(
        regex=r'^\+?1?\d{9,15}$',
        error_messages={'invalid': "Enter a valid phone number."},
        required=True
    )
