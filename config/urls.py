from django.contrib import admin
from django.urls import path
from core.views import home, devenir_benevole, contact, mentions_legales

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name='home'),
    path('devenir-benevole/', devenir_benevole, name='devenir_benevole'),
    path('contact/', contact, name='contact'),
    path('mention-legales/', mentions_legales, name='mentions légales')
]