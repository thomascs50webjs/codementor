from django.contrib import admin
from django.urls import path, include
from app import views 
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name = "index"),
    # path("login", views.login_view, name="login"),
    path('login-redirect/', views.login_redirect_view, name='login_redirect'),
    path("logout", views.logout_view, name="logout"),
    path(
        'reset/<uidb64>/<token>/',
        views.password_reset_from_key,
        name='password_reset_from_key'
    ),
    path('settings', views.settings, name="settings"),
    path('delete_pen/<int:pen_id>/', views.delete_pen, name='delete_pen'),
    path("main", views.main, name = "main"),
    path("create", views.create, name="create"),
    path("saved", views.saved, name = "saved"),
    path("pen/", views.pen, name="pen"),
    path('edit/<int:pen_id>/', views.code, name='edit_pen'),
    path("base", views.base, name="base"),
    path('projects/', views.projects, name='projects'),
    path("save-pen/", views.save_current_pen, name="save_current_pen"),
    path('save_pen_title/', views.save_pen_title, name='save_pen_title'),
    path('onboarding/', views.onboarding, name='onboarding'),
    path('onboarding/submit/', views.onboarding_submit, name='onboarding_submit'),
    path('onboarding/auto-save/', views.onboarding_auto_save, name='onboarding_auto_save'),
    path('help-center/', views.help_center, name='help_center'),
    path('about/', views.about, name='about'),
    path('policy/', views.policy, name='policy'),
    path('library/', views.library, name='library'),
    path('profile/', views.profile, name='profile'),
    path('fork/<int:pen_id>/', views.fork_pen, name='fork_pen'),
    path('save_fork/', views.save_fork, name='save_fork'),
    path('save_edit/', views.save_edit, name='save_edit'),
    path('increment_view/<int:pen_id>/', views.increment_view, name='increment_view'),
    path('accounts/', include('allauth.urls')),
     path("switch-account/", views.switch_account_view, name="switch_account"),
     path("delete-account/", views.delete_account, name="delete_account"),
         path('profile/upload-picture/', views.upload_profile_picture, name='upload_profile_picture'),

     

    
]

if settings.DEBUG:  # Only serve media files in development
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
