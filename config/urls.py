from django.contrib import admin
from django.urls import path
from core.views import home, devenir_benevole, contact, mentions_legales, reglementation
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name='home'),
    path('devenir-benevole/', devenir_benevole, name='devenir_benevole'),
    path('contact/', contact, name='contact'),
    path('mention-legales/', mentions_legales, name='mentions legales'),

    path('connexion/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('deconnexion/', auth_views.LogoutView.as_view(), name='logout')
]