from django.shortcuts import render
from django.contrib.auth.models import User
from .models import Actualite, Materiel

def home(request):
    # Compter les membres actifs
    nb_benevoles = User.objects.filter(is_active=True).count()
    
    # Compter uniquement les matériels de catégorie VEHICULE qui sont en service
    nb_vehicules = Materiel.objects.filter(categorie='VEHICULE', en_service=True).count()
    
    # Récupérer les 3 dernières actus
    actus = Actualite.objects.all().order_by('-date_publication')[:3]
    
    context = {
        'nb_benevoles': nb_benevoles,
        'nb_vehicules': nb_vehicules,
        'actus': actus,
    }
    return render(request, 'index.html', context)