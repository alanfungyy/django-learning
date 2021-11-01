from django.contrib.auth.models import AbstractUser
from django.db import models
from django import forms

# Models
class User(AbstractUser):
    def __str__(self):
        return self.username

class Listing(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(verbose_name="Listing Title", max_length=128)
    description = models.CharField(verbose_name="Listing Description", max_length=256)
    price = models.IntegerField()
    url = models.URLField(verbose_name="URL", max_length=256, blank=True)
    category = models.CharField(max_length=128, blank=True)
    datetime_created = models.DateTimeField(verbose_name="Listing Created", auto_now_add=True)
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.title

class Bid(models.Model):
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    price = models.IntegerField()
    datetime_created = models.DateTimeField(verbose_name="Bid Placed", auto_now_add=True)

    def __str__(self):
        return str(self.price)

class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE)
    title = models.CharField(verbose_name="Comment Title", max_length=128)
    comment = models.CharField(max_length=256)
    datetime_created = models.DateTimeField(verbose_name="Comment Created", auto_now_add=True)

    def __str__(self):
        return self.title

class Watchlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE)


# Modelforms
class ListingForm(forms.ModelForm):
    class Meta:
        model = Listing
        exclude = ['user']
        widgets = {
            'description': forms.Textarea(attrs={'cols': 80, 'rows': 8}),
        }

class BidForm(forms.ModelForm):
    class Meta:
        model = Bid
        fields = ['price']
        widgets = {
            'price': forms.TextInput(attrs={'placeholder': 'Bid', 'autocomplete': 'off', 'autofocus': 'autofocus required', 'class': 'form-control'})
        }
        labels = {
            'price': '',
        }

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        exclude = ['user', 'listing']
        widgets = {
            'comment': forms.Textarea(attrs={'cols': 80, 'rows': 8}),
        }

class WatchlistForm(forms.ModelForm):
    class Meta:
        model = Watchlist
        exclude = ['user', 'listing']
