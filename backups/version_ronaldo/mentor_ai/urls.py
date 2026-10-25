from django.contrib import admin
from django.urls import path
from app import views 

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name = "index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("main", views.main, name = "main"),
    path("create", views.create, name="create"),
    path("saved", views.saved, name = "saved"),
    path("pen/", views.pen, name="pen"),
    path('edit/<int:pen_id>/', views.code, name='edit_pen'),
    path("base", views.base, name="base"),
    path('projects/', views.projects, name='projects'),
    path("save-pen/", views.save_current_pen, name="save_current_pen"),
    path('save_pen_title/', views.save_pen_title, name='save_pen_title'),





]
