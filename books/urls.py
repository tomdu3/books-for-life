from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('user_page/', views.user_page, name='user_page'),
    path('user_favourites/', views.user_favourites, name='user_favourites'),
    path('summernote/', include('django_summernote.urls')),
    path('details/<slug:slug>/',
         views.BookDetail.as_view(), name='book_detail'),
    path('edit/<slug:slug>', views.BookUpdateView.as_view(), name='book_edit'),
    path('add/', views.AddBookView.as_view(), name='book_add'),
    path('<slug:slug>/delete/', views.BookDeleteView.as_view(),
         name='book_delete'),
    path('find_book/', views.find_book, name='find_book'),
    path('delete/<int:book_id>/',
         views.book_delete_confirmation, name='book_delete_confirmation'),
    path('like_book/<slug:slug>/', views.like_book, name='like_book'),
    path('like_book_detail/<slug:slug>/', views.like_book_detail,
         name='like_book_detail'),
    path('remove_from_favourites/<str:slug>/', views.remove_from_favourites,
         name='remove_from_favourites'),
]
