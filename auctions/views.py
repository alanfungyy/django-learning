from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django import forms
from django.db.models.functions import Lower
from django.contrib import messages

from .models import User, Listing, Bid, Comment, Watchlist, ListingForm, BidForm, CommentForm, WatchlistForm


def index(request):
    # listings = Listing.objects.filter(active="True").order_by("-datetime_created")

    listings = list(Listing.objects.filter(active="True").order_by("-datetime_created"))
    bid_listings = [value['listing'] for value in list(Bid.objects.values('listing').distinct())]
    for listing in listings:
        if listing.pk in bid_listings:
            listing.current_price =  str(Bid.objects.filter(listing=listing.pk).order_by('-price').first())
        else:
            listing.current_price =  listing.price

    return render(request, "auctions/index.html", {"listings": listings})


def past(request):
    listings = Listing.objects.filter(active="False").order_by("-datetime_created")
    bid_listings = [value['listing'] for value in list(Bid.objects.values('listing').distinct())]
    for listing in listings:
        if listing.pk in bid_listings:
            listing.current_price =  str(Bid.objects.filter(listing=listing.pk).order_by('-price').first())
        else:
            listing.current_price =  listing.price
    return render(request, "auctions/past.html", {"listings": listings})


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            request.session["user"] = username
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    # Log out user
    logout(request)

    # Clear session data
    request.session.flush()
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        request.session["user"] = username
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")


@login_required
def createlisting(request):
    if request.method == "POST":
        form = ListingForm(request.POST)

        if form.is_valid():
            try:
                updated_form = form.save(commit=False)
                updated_form.user_id = request.POST.get("user_id")
                updated_form.save()

            except Exception as e:
                return render(request, "auctions/createlisting.html", {"form": form, "message": e})

            return HttpResponseRedirect(reverse("index"))

        else:
            return render(request, "auctions/createlisting.html", {"form": form, "message": "Invalid data!"})

    else:
        f = ListingForm()
        return render(request, "auctions/createlisting.html", {"form": f})


def listing(request, pk):
    # Get the relevant listing & comments by PK
    listing = Listing.objects.get(pk=pk)
    comments = Comment.objects.filter(listing=pk)

    # Get current price, total bids & check highest bidder status
    if len(Bid.objects.filter(listing=listing)) > 0:
        current_price = Bid.objects.filter(listing=listing).order_by('-price')[0].price
        if "user" in request.session:
            highest_bidder = str(Bid.objects.filter(listing=listing).order_by('price')[0].user) == request.session["user"]
        else:
            highest_bidder = False
    else:
        current_price = Listing.objects.get(pk=pk).price
        highest_bidder = False
    total_bids = Bid.objects.filter(listing=listing).count()

    # Get the forms for comment and bid
    commentform = CommentForm()
    bidform = BidForm()

    # Check status for watchlist, active listing and creatorship

    is_active = Listing.objects.get(pk=pk).active
    if "user" in request.session:
        userid = User.objects.get(username=request.session["user"])
        in_watchlist = len(Watchlist.objects.filter(listing_id=pk).filter(user_id=userid)) > 0
        is_creator = str(Listing.objects.get(pk=pk).user) == request.session["user"]
    else:
        is_creator = False
        in_watchlist = False

    return render(request, "auctions/listing.html", {
        "listing": listing,
        "commentform": commentform,
        "comments": comments,
        "in_watchlist": in_watchlist,
        "bidform": bidform,
        "current_price": current_price,
        "total_bids": total_bids,
        "highest_bidder": highest_bidder,
        "is_active": is_active,
        "is_creator": is_creator,
        })

@login_required
def postcomment(request, pk):
    if request.method == "POST":
        comment = CommentForm(request.POST)

        if comment.is_valid():
            try:
                updated_commentform = comment.save(commit=False)
                updated_commentform.user_id = request.POST.get("user_id")
                updated_commentform.listing_id = request.POST.get("listing")
                updated_commentform.save()

            except Exception as e:
                return render(request, "auctions/listing.html", {"comment": comment, "message": e})

            return HttpResponseRedirect(reverse("listing", kwargs={'pk': pk}))

        else:
            return render(request, "auctions/listing.html", {"comment": comment, "message": "Comment error!"})

@login_required
def delete(request, pk):
    # Delete post
    if request.method == "POST":
        Listing.objects.get(pk=pk).delete()
        return HttpResponseRedirect(reverse("index"))

def categories(request):
    # Get the list of distinct categories while being case insensitive
    queryset_list = Listing.objects.filter(active="True").annotate(categories_lower=Lower("category")).values("categories_lower").distinct()
    categories = [queryset for queryset in queryset_list if queryset]
    return render(request, "auctions/categories.html", {"categories": categories})

def category(request, category):
    # Get listing under the category
    category_list = Listing.objects.filter(active="True").filter(category__icontains=category)
    return render(request, "auctions/category.html", {"category_list": category_list, "category": category})

@login_required
def watchlist(request, username):
    if request.method == "POST":
        listing = request.POST.get("listing")
        user = request.POST.get("user_id")

        try:
            w = WatchlistForm(request.POST)
            watchlist = w.save(commit=False)
            watchlist.user_id = user
            watchlist.listing_id = listing
            watchlist.save()
        except Exception as e:
            return render(request, "auctions/listing.html", {"message": e})
        return HttpResponseRedirect(reverse("watchlist", kwargs={"username": username}))

    else:
        user = User.objects.get(username=username)
        try:
            watchlist = Watchlist.objects.filter(user_id=user)
        except Exception as e:
            return render(request, "auctions/watchlist.html", {"message": e})
        return render(request, "auctions/watchlist.html", {"watchlist": watchlist})

@login_required
def removewatchlist(request):
    user_id = request.POST.get("user_id")
    listing = request.POST.get("listing")

    if request.method == "POST":
        Watchlist.objects.filter(user_id=user_id).get(listing_id=listing).delete()
        return HttpResponseRedirect(reverse("listing", kwargs={"pk": listing}))

@login_required
def bid(request, listing):
    if request.method == "POST":
        # Assign bid price and valid_price variable
        bid_price = int(request.POST.get("price"))
        valid_price = False

        # Assign current price and check if bid price is valid
        if len(Bid.objects.filter(listing=listing)) > 0:
            current_price = Bid.objects.filter(listing=listing).order_by('-price')[0].price
            if bid_price > current_price:
                valid_price = True
        else:
            current_price = Listing.objects.get(pk=listing).price
            if bid_price >= current_price:
                valid_price = True

        # Record bid if bid price is valid
        if valid_price:
            b = BidForm(request.POST)

            if b.is_valid():
                bidform = b.save(commit=False)
                bidform.listing_id = listing
                bidform.user_id = request.POST.get("user_id")
                bidform.save()
                return HttpResponseRedirect(reverse("listing", kwargs={"pk":listing}))

            else:
                messages.error(request, "Bid is invalid!")
                return HttpResponseRedirect(reverse("listing", kwargs={"pk": listing}))

        else:
            messages.error(request, "Your bid is too low!")
            return HttpResponseRedirect(reverse("listing", kwargs={"pk": listing}))

        return HttpResponseRedirect(reverse("listing", kwargs={"pk": listing}))

@login_required
def close(request, pk):
    # Close listing
    if request.method == "POST":
        close = Listing.objects.get(pk=pk)
        close.active = False
        close.save()
        return HttpResponseRedirect(reverse("index"))

@login_required
def user(request, user):
    # Get list of listings by user
    id = User.objects.get(username=user)
    user_listings = Listing.objects.filter(user=id)

    # Get list of won bids by user
    all_listings = list(Listing.objects.all())
    bid_listings = [value['listing'] for value in list(Bid.objects.values('listing').distinct())]
    winning_bids = []
    for listing in all_listings:
        if listing.pk in bid_listings:
            if str(Bid.objects.filter(listing=listing.pk).order_by('-price').first().user) == user:
                winning_bids.append(Listing.objects.get(pk=listing.pk))

    return render(request, "auctions/user.html", {
        "user": user,
        "listings": user_listings,
        "winning_bids": winning_bids,
        })
