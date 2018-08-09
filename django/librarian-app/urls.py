from django.urls import path
from . import views

urlpatterns = [
    path('', 
         views.search_books),
    path('newuser/', 
         views.add_user),
    path('checkout/', 
         views.checkout),
    path('checkin/', 
         views.checkin),
    path('fines/', 
         views.fines)
]