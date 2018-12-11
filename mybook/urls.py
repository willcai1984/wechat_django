from django.urls import path
from . import views

app_name = 'mybook'

urlpatterns = [
    path('add_book', views.add_book, name='add_book'),
    path('show_books', views.show_books, name='show_books'),
]
