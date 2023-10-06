from django.contrib.auth.models import AbstractUser
from django.db import models
import timeago, datetime
import math
from django.core.validators import MaxLengthValidator, MinLengthValidator

class User(AbstractUser):
    watchlist = models.ManyToManyField("Listing", blank=True, related_name="watchlist")

    @property
    def created(self):
        return timeago.format(self.date_joined, datetime.datetime.now())

    @property
    def highest_bids(self):
        all_bids_by_user = Bid.objects.filter(bidder=self)
        listings_with_bids_by_user = []
        for bid in all_bids_by_user:
            listings_with_bids_by_user.append(bid.listing)
        highest_bids = set()
        for listing in listings_with_bids_by_user:
            bids_by_user = listing.bids.filter(bidder=self)
            highest_bid_value = max(bid.value for bid in bids_by_user)
            highest_bid_by_user = Bid.objects.get(bidder=self, value=highest_bid_value, listing=listing)
            highest_bids.add(highest_bid_by_user)
        return highest_bids

    @property
    def open_highest_bids(self):
        open_highest_bids = []
        for bid in self.highest_bids:
            if bid.listing.status == "1":
                open_highest_bids.append(bid)
        return open_highest_bids

    @property
    def closed_highest_bids(self):
        closed_highest_bids = []
        for bid in self.highest_bids:
            if bid.listing.status == "2":
                closed_highest_bids.append(bid)
        return closed_highest_bids

class Listing(models.Model):
    title = models.CharField(max_length=50)
    description = models.CharField(max_length=1000)
    starting_bid = models.DecimalField(max_digits=8, decimal_places=2)
    photo = models.URLField(max_length=400, blank="True")
    lister = models.ForeignKey("User", on_delete=models.PROTECT, related_name="listings", )
    category = models.ForeignKey("Category", on_delete=models.PROTECT, related_name="listings", null=True, blank=True)
    created_datetime = models.DateTimeField(blank=True)
    contact = models.CharField(max_length=9, validators=[MaxLengthValidator(9),MinLengthValidator(9)])

    @property
    def created(self):
        return timeago.format(self.created_datetime, datetime.datetime.now(datetime.timezone.utc))
    
    date_closed_datetime = models.DateTimeField(blank= True, null=True)

    @property
    def date_closed(self):
        return timeago.format(self.date_closed_datetime, datetime.datetime.now(datetime.timezone.utc))

    STATUS_CHOICES = (
        ('1', 'Active'),
        ('2', 'Closed'),
    )
    status = models.CharField(max_length = 1, choices=STATUS_CHOICES, default="1")

    @property
    def number_of_bids(self):
        bids = self.bids.count()
        if bids is not 0:
            if bids == 1:
                return f"{bids} Bid"
            else:
                return f"{bids} Bids"
        else:
            return f"No Bids"

    @property
    def number_of_comments(self):
        comments = self.comments.count()
        if comments == 1:
            return f"{comments} Comment"
        else:
            return f"{comments} Comments"

    @property
    def highest_bid(self):
        bids = self.bids.all()
        if len(bids) > 0:
            return self.bids.get(value = max(bid.value for bid in bids ))
        else:
            return False

    def new_bid_min_value(self):
        min = math.ceil(float(self.highest_bid.value) + 0.01)
        return min

    def highest_bid_by_user(self, user):
        bids_by_user = self.bids.filter(bidder=user)
        if bids_by_user:
            highest_bid = self.bids.get(value = max(bid.value for bid in bids_by_user ))
            return highest_bid
        else:
            return False

    def __str__ (self):
        return f"{self.title} by {self.lister}"

class Category(models.Model):
    name = models.CharField(max_length=20)

    def __str__ (self):
        return f"{self.name}"

class Bid(models.Model):
    value = models.DecimalField(max_digits=8, decimal_places=2)
    listing = models.ForeignKey("Listing", on_delete=models.CASCADE, related_name="bids")
    bidder =  models.ForeignKey("User", on_delete=models.PROTECT, related_name="bids")
    created_datetime = models.DateTimeField(blank=True)

    @property
    def created(self):
        return timeago.format(self.created_datetime, datetime.datetime.now(datetime.timezone.utc))

    @property
    def status(self):
        if self.listing.status == "1":
            if self == self.listing.highest_bid:
                return "Highest"
            else:
                return "Out-bidded"
        else:
            if self == self.listing.highest_bid:
                return "Won"
            else:
                return "Lost"
        

    def __str__ (self):
        return f"{self.listing}: ${self.value} by {self.bidder}"

class Comment(models.Model):
    content = models.CharField(max_length=100, blank=False)
    listing = models.ForeignKey("Listing", on_delete=models.CASCADE, related_name="comments")
    commenter = models.ForeignKey("User", on_delete=models.CASCADE, related_name="comments")
    created_datetime = models.DateTimeField(blank=True)

    @property
    def created(self):
        return timeago.format(self.created_datetime, datetime.datetime.now(datetime.timezone.utc))

    def __str__ (self):
        return f"{self.content} by {self.commenter}"
