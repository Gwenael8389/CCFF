from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from .models import Actualite, Materiel, RisqueIncendie, Candidature

def home(request):
    nb_benevoles = User.objects.filter(is_active=True).count()
    nb_vehicules = Materiel.objects.filter(categorie='VEHICULE', en_service=True).count()
    actus = Actualite.objects.all().order_by('-date_publication')[:3]
    
    # On récupère le dernier risque enregistré, sinon on en crée un par défaut
    risque_actuel = RisqueIncendie.objects.last()
    
    context = {
        'nb_benevoles': nb_benevoles,
        'nb_vehicules': nb_vehicules,
        'actus': actus,
        'risque_actuel': risque_actuel,
    }
    return render(request, 'index.html', context)

def devenir_benevole(request):
    if request.method == 'POST':
        # Si le formulaire est envoyé, on sauvegarde en base de données
        Candidature.objects.create(
            nom=request.POST.get('nom'),
            prenom=request.POST.get('prenom'),
            email=request.POST.get('email'),
            telephone=request.POST.get('telephone'),
            message=request.POST.get('message')
        )
        # On affiche un petit message de succès et on renvoie à l'accueil
        messages.success(request, "Votre candidature a bien été envoyée ! Nous vous recontacterons vite.")
        return redirect('home')
        
    return render(request, 'benevole.html')