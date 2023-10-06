from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("categories", views.categories, name="categories"),
    path("my_bids", views.my_bids, name="my_bids"),
    path("my_watchlist", views.my_watchlist, name="my_watchlist"),
    path("categories/<int:category_id>", views.category, name="category"),
    path("<int:listing_id>", views.listing, name="listing"),
    path("account/<int:account_id>", views.account, name="account"),
    path("my_account", views.my_account, name="my_account"),
    path("edit_account", views.edit_account, name="edit_account"),
    path("edit_password", views.edit_password, name="edit_password"),
    path("new_listing", views.new_listing, name="new_listing"),
    path("<int:listing_id>/add_comment", views.add_comment, name="add_comment"),
    path("<int:listing_id>/place_bid", views.place_bid, name="place_bid"),
    path("<int:listing_id>/add_to_watchlist", views.add_to_watchlist, name="add_to_watchlist"),
    path("<int:listing_id>/remove_from_watchlist", views.remove_from_watchlist, name="remove_from_watchlist"),
    path("<int:listing_id>/close_auction", views.close_auction, name="close_auction"),


]

"""    path("search/", views.search, name="search"),"""