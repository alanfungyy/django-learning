from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("createlisting", views.createlisting, name="createlisting"),
    path("listing/<int:pk>", views.listing, name="listing"),
    path("<int:pk>", views.postcomment, name="postcomment"),
    path("delete/<int:pk>", views.delete, name="delete"),
    path("category/", views.categories, name="categories"),
    path("category/<str:category>", views.category, name="category"),
    path("watchlist/<str:username>", views.watchlist, name="watchlist"),
    path("removewatchlist/", views.removewatchlist, name="removewatchlist"),
    path("bid/<int:listing>", views.bid, name="bid"),
    path("close/<int:pk>", views.close, name="close"),
    path("past/", views.past, name="past"),
    path("<str:user>", views.user, name="user"),
]
