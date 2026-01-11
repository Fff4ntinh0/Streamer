from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register, name="register"),
    path('', views.login, name="login"),
    path('create/', views.create, name="create"),
    path('logout/', views.logout, name="logout"),
    path('config/', views.config, name="config"),
    path('configout/', views.configout, name="configout"),
    path('catalog/', views.catalog, name="catalog"),
    path('film/<int:id>/', views.film_detail, name="film_detail"),
    path('comment/<int:title_id>/', views.comment, name="comment")
]