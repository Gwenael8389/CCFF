from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as auth_views
from core.views import home, devenir_benevole, contact, mentions_legales, reglementation, missions, actualites, galerie, soutenir, intranet, planning, inscription_patrouille,supprimer_patrouille, carte_dfci

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name='home'),
    path('devenir-benevole/', devenir_benevole, name='devenir_benevole'),
    path('contact/', contact, name='contact'),
    path('mentions-legales/', mentions_legales, name='mentions_legales'),
    path('reglementation/', reglementation, name='reglementation'),
    path('soutenir/', soutenir, name='soutenir'),
    path('intranet/', intranet, name='intranet'),
    path('intranet/planning/', planning, name='planning'),
    path('intranet/planning/inscription/<int:patrouille_id>/', inscription_patrouille, name='inscription_patrouille'),
    path('intranet/planning/', planning, name='planning'),
    path('intranet/planning/annuler/<int:patrouille_id>/', supprimer_patrouille, name='supprimer_patrouille'),
    path('intranet/carte/', carte_dfci, name='carte_dfci'),
    path('intranet/carte/', carte_dfci, name='carte_dfci'),
    
    path('missions/', missions, name='missions'),
    path('actualites/', actualites, name='actualites'),
    path('galerie/', galerie, name='galerie'),
    
    path('connexion/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('deconnexion/', auth_views.LogoutView.as_view(), name='logout'),
]