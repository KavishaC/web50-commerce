from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse
from django.db.models import Avg, Max, Min
import datetime
from django.utils import timezone
from operator import itemgetter
from django.contrib.auth.decorators import login_required

from .models import User, Listing, Category, Bid, Comment

def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
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
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")

def index(request):
    listings = Listing.objects.filter(status="1")
    return render(request, "auctions/index.html", {
        "title": "Active Listings",
        "listings": listings,
    })

def categories(request):
    return render(request, "auctions/categories.html", {
        "categories": Category.objects.all(),
    })

@login_required
def my_bids(request):
    return render(request, "auctions/bids.html", {
        "open_bids": request.user.open_highest_bids,
        "closed_bids": request.user.closed_highest_bids,
        "categories": Category.objects.all(),
    })

@login_required
def my_watchlist(request):
    return render(request, "auctions/index.html", {
        "title": "My Watchlist",
        "listings": request.user.watchlist.all(),
    })

@login_required
def edit_account(request):
    if request.method == "POST":
        user = request.user
        username = request.POST["username"]
        email = request.POST["email"]

        user.username = username
        user.email = email
        user.save()

        messages.success(request, "Your account was changed successfully")
        return HttpResponseRedirect(reverse("my_account"))

    else:
        return render(request, "auctions/edit_account.html")


@login_required
def edit_password(request):
    if request.method == "POST":

        username = request.POST["username"]
        password = request.POST["password"]
        new_password = request.POST["new_password"]
        confirmation = request.POST["confirmation"]

        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            
            if new_password == confirmation:
                user.set_password(new_password)

                messages.success(request, "Your password was changed successfully")
                return HttpResponseRedirect(reverse("my_account"))

            else:
                
                return render(request, "auctions/edit_password.html", {
                "message": "Passwords do not match."
            })


        else:
            return render(request, "auctions/edit_password.html", {
                "message": "Invalid username and/or password."
            })



    else:
        return render(request, "auctions/edit_password.html")

def category(request, category_id):
    category = Category.objects.get(pk=category_id)
    listings = Listing.objects.filter(category=category)
    return render(request, "auctions/index.html", {
        "title": category,
        "listings": listings,
    })

def listing(request, listing_id):
    listing = Listing.objects.get(pk=listing_id)
    user = request.user
    lost = None

    if user.is_authenticated:
        highest = listing.highest_bid_by_user(user=user)

        if listing.lister == user:
            if listing.status == "2":
                highest_bid = listing.highest_bid
                if highest_bid:
                    messages.success(request, f"Auction successfully closed! Please contact highest bidder: {highest_bid.bidder} to move forward with the sale.")
                else:
                    messages.success(request, f"Auction successfully closed! No bids were placed")

        if highest:
            if listing.status == "1":
                if highest == listing.highest_bid:
                    messages.info(request, "Your bid is currently the highest!")
                else:
                    messages.warning(request, "You have been out-bidded! You can place another bid below.")

            elif listing.status == "2":
                if highest == listing.highest_bid:
                    messages.success(request, "Congratulations! You won the auction. Please contact seller to move forward with the sale.")
                else:
                    messages.error(request, "Sorry, You lost the auction.")
                    lost = True

    return render(request, "auctions/listing.html", {
        "listing": listing,
        "lost": lost,
    })


@login_required
def my_account(request):
    user = request.user

    active_listings = []
    closed_listings = []

    for listing in user.listings.all():
        if listing.status == "1":
            active_listings.append(listing)
        elif listing.status == "2":
            closed_listings.append(listing)

    return render(request, "auctions/my_account.html", {
        "active_listings": active_listings,
        "closed_listings": closed_listings,
    })

def account(request, account_id):

    account = User.objects.get(id=account_id)

    if account == request.user:
        return HttpResponseRedirect(reverse("my_account"))

    username = account.username
    id = account.id
    email = account.email

    return render(request, "auctions/account.html", {
        "account": account,
    })

@login_required
def new_listing(request):
    if request.method == "POST":
        title = request.POST["title"]
        category = Category.objects.get(name=request.POST["category"])
        lister =  request.user
        starting_bid = request.POST["starting_bid"]
        contact = request.POST["contact"]
        image_url = request.POST["image_url"]
        description = request.POST["description"]
        now = timezone.now()

        new_listing = Listing(title=title, category=category, lister=lister, starting_bid=starting_bid, contact=contact, photo=image_url, description=description, created_datetime=now)
        new_listing.save()
        messages.success(request, "Success! Your listing was created.")

        return HttpResponseRedirect(reverse("listing", args=(new_listing.id, )))


    else:
        return render(request, "auctions/new_listing.html", {
            "categories": Category.objects.all(), 
        })

@login_required
def add_comment(request, listing_id):
    if request.method == "POST":
        commenter = request.user
        listing = Listing.objects.get(pk=listing_id)
        content = request.POST["content"]
        now =timezone.now()
        comment = Comment(content=content, listing=listing, commenter=commenter, created_datetime=now)
        comment.save()
        return redirect(f"/{listing_id}")

@login_required
def place_bid(request, listing_id):
    if request.method == "POST":
        bidder = request.user
        bid_value = request.POST["new_bid_value"]
        listing = Listing.objects.get(pk=listing_id)
        now = timezone.now()
        new_bid = Bid(value=bid_value, listing=listing, bidder=bidder, created_datetime=now)
        new_bid.save()
        return redirect(f"/{listing_id}")

@login_required
def add_to_watchlist(request, listing_id):
    if request.method == "POST":
        listing = Listing.objects.get(pk=listing_id)
        user = request.user
        user.watchlist.add(listing)
        return redirect(f"/{listing_id}")

@login_required
def remove_from_watchlist(request, listing_id):
    if request.method == "POST":
        listing = Listing.objects.get(pk=listing_id)
        user = request.user
        user.watchlist.remove(listing)
        return redirect(f"/{listing_id}")

@login_required
def close_auction(request, listing_id):
    user = request.user
    listing = Listing.objects.get(pk=listing_id)
    
    if request.method == "POST" and user == listing.lister:
        listing.status = "2"
        listing.date_closed_datetime = timezone.now()
        listing.save()
        return HttpResponseRedirect(reverse("listing", args=(listing.id, )))




"""
def search(request):
    if request.method == "POST":
        query = request.POST["query"]
        listings_with_query_in_title = Listing.objects.filter(title__icontains=query)
        listings_with_query_in_description = Listing.objects.filter(description__icontains=query)
        listings_with_query_in_lister = User.objects.filter(username__contains=query)

        listings = listings_with_query_in_title | listings_with_query_in_description 
        return render(request, "auctions/search.html", {
            "query": query,
            "listings": listings,
        })"""


"""
listings_with_query_in_lister = Listing.objects.filter(lister=(listing.lister for listing in listers_with_query_in_username))
"""