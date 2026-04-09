from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from .models import Actualite, Materiel, RisqueIncendie, Candidature, MessageContact, PhotoGalerie, MembreEquipe, DocumentIntranet
from django.contrib.auth.decorators import login_required

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
        
    return render(request, 'devenir-benevole.html')

def contact(request):
    if request.method == 'POST':
        MessageContact.objects.create(
            nom=request.POST.get('nom'),
            email=request.POST.get('email'),
            sujet=request.POST.get('sujet'),
            message=request.POST.get('message')
        )
        messages.success(request, "Votre message a bien été envoyé. Nous vous répondrons dans les plus brefs délais.")
        return redirect('contact')
        
    return render(request, 'contact.html')

def mentions_legales(request):
    return render(request, 'mention-legales.html')

def reglementation(request):
    return render(request, 'reglementation.html')

def missions(request):
    vehicules = Materiel.objects.filter(categorie='VEHICULE', en_service=True)
    radios = Materiel.objects.filter(categorie='RADIO', en_service=True)
    outils = Materiel.objects.filter(categorie='OUTIL', en_service=True)
    equipe = MembreEquipe.objects.all()
    
    return render(request, 'missions.html', {
        'vehicules': vehicules,
        'radios': radios,
        'outils': outils,
        'equipe': equipe
    })

def actualites(request):
    toutes_les_actus = Actualite.objects.all().order_by('-date_publication')
    return render(request, 'actualites.html', {'actus': toutes_les_actus})

def galerie(request):
    photos = PhotoGalerie.objects.all().order_by('-date_ajout')
    return render(request, 'galerie.html', {'photos': photos})

def soutenir(request):
    return render(request, 'soutenir.html')

@login_required(login_url='/connexion/')
def intranet(request):
    documents = DocumentIntranet.objects.all().order_by('-date_ajout')
    return render(request, 'intranet.html', {'documents': documents})