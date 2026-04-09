from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib import messages
from .models import Actualite, Materiel, RisqueIncendie, Candidature, MessageContact, PhotoGalerie, MembreEquipe, DocumentIntranet, Patrouille, User
from django.contrib.auth.decorators import login_required
from datetime import date
from django.utils import timezone
from django.db.models import Q
import calendar

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
    user = request.user
    annee_en_cours = date.today().year

    # Mise à jour : on cherche les patrouilles où l'utilisateur est soit Chef, soit Coéquipier
    mes_patrouilles = Patrouille.objects.filter(Q(chef_de_bord=user) | Q(coequipier=user), date_patrouille__year=annee_en_cours)
    nb_mes_patrouilles = mes_patrouilles.count()
    prochaine_patrouille = Patrouille.objects.filter(Q(chef_de_bord=user) | Q(coequipier=user), date_patrouille__gte=date.today()).order_by('date_patrouille').first()

    total_patrouilles_ccff = Patrouille.objects.filter(date_patrouille__year=annee_en_cours).count()
    documents = DocumentIntranet.objects.all().order_by('-date_ajout')

    context = {
        'nb_mes_patrouilles': nb_mes_patrouilles,
        'prochaine_patrouille': prochaine_patrouille,
        'total_patrouilles_ccff': total_patrouilles_ccff,
        'documents': documents,
        'annee_en_cours': annee_en_cours,
    }
    return render(request, 'intranet.html', context)

@login_required(login_url='/connexion/')
def planning(request):
    annee = timezone.now().year
    mois_actuel = timezone.now().month

    # 1. GESTION DE LA NAVIGATION DES MOIS (Juin à Septembre)
    try:
        mois_selectionne = int(request.GET.get('mois', mois_actuel))
        # Si on est hors saison ou qu'on triche avec l'URL, on force entre Juin (6) et Septembre (9)
        if mois_selectionne not in [6, 7, 8, 9]:
            mois_selectionne = 6 if mois_actuel < 6 else (9 if mois_actuel > 9 else mois_actuel)
    except ValueError:
        mois_selectionne = 6

    # 2. SOUMISSION DU FORMULAIRE (Inscription)
    if request.method == 'POST':
        date_p = request.POST.get('date_patrouille')
        heure_d = request.POST.get('heure_debut')
        heure_f = request.POST.get('heure_fin')
        type_p = request.POST.get('type_patrouille')
        coequipier_id = request.POST.get('coequipier')
        vehicule_id = request.POST.get('vehicule')

        nouvelle_patrouille = Patrouille(
            date_patrouille=date_p, heure_debut=heure_d, heure_fin=heure_f,
            type_patrouille=type_p, chef_de_bord=request.user
        )
        if coequipier_id: nouvelle_patrouille.coequipier_id = coequipier_id
        if vehicule_id: nouvelle_patrouille.vehicule_id = vehicule_id

        nouvelle_patrouille.save()
        messages.success(request, "Votre patrouille a été ajoutée au planning !")
        # On redirige vers le même mois pour ne pas perdre l'utilisateur
        return redirect(f'/intranet/planning/?mois={mois_selectionne}')

    # 3. GÉNÉRATION DU CALENDRIER VISUEL
    patrouilles_du_mois = Patrouille.objects.filter(date_patrouille__year=annee, date_patrouille__month=mois_selectionne)
    
    # On trie intelligemment en mémoire pour ne pas surcharger la base de données
    jours_mes_patrouilles = set()
    jours_autres_patrouilles = set()
    
    for p in patrouilles_du_mois:
        if p.chef_de_bord == request.user or p.coequipier == request.user:
            jours_mes_patrouilles.add(p.date_patrouille)
        else:
            jours_autres_patrouilles.add(p.date_patrouille)

    # Création de la matrice du calendrier
    cal = calendar.Calendar(firstweekday=0) # Semaine commence le Lundi
    jours_mois = cal.itermonthdates(annee, mois_selectionne)
    
    calendrier_data = []
    aujourdhui = date.today()

    for jour in jours_mois:
        if jour.month != mois_selectionne:
            calendrier_data.append({'hors_mois': True}) # Cases vides du calendrier
        else:
            calendrier_data.append({
                'date': jour,
                'hors_mois': False,
                'passe': jour < aujourdhui,
                'mes_patrouilles': jour in jours_mes_patrouilles,
                'autres_patrouilles': jour in jours_autres_patrouilles,
            })

    # 4. DONNÉES GLOBALES POUR LA PAGE
    patrouilles_futures = Patrouille.objects.filter(date_patrouille__gte=aujourdhui).order_by('date_patrouille', 'heure_debut')
    benevoles = User.objects.filter(is_active=True).exclude(id=request.user.id)
    vehicules = Materiel.objects.filter(categorie='VEHICULE', en_service=True)
    mois_noms = {6: 'Juin', 7: 'Juillet', 8: 'Août', 9: 'Septembre'}

    return render(request, 'planning.html', {
        'calendrier': calendrier_data,
        'mois_selectionne': mois_selectionne,
        'mois_noms': mois_noms,
        'patrouilles': patrouilles_futures,
        'benevoles': benevoles,
        'vehicules': vehicules,
        'date_min': f"{annee}-06-01",
        'date_max': f"{annee}-09-30",
    })

@login_required(login_url='/connexion/')
def inscription_patrouille(request, patrouille_id):
    # Cette vue ne renvoie pas de page HTML, elle fait l'action puis redirige
    patrouille = get_object_or_404(Patrouille, id=patrouille_id)
    
    if request.user in patrouille.benevoles.all():
        # Si le bénévole est déjà dedans, on le retire
        patrouille.benevoles.remove(request.user)
        messages.success(request, f"Vous êtes désinscrit de la patrouille du {patrouille.date_patrouille.strftime('%d/%m')}.")
    else:
        # Sinon on l'ajoute
        patrouille.benevoles.add(request.user)
        messages.success(request, f"Vous êtes inscrit à la patrouille du {patrouille.date_patrouille.strftime('%d/%m')} !")
        
    return redirect('planning')

@login_required(login_url='/connexion/')
def carte_dfci(request):
    return render(request, 'carte.html')

@login_required(login_url='/connexion/')
def supprimer_patrouille(request, patrouille_id):
    patrouille = get_object_or_404(Patrouille, id=patrouille_id)
    if patrouille.chef_de_bord == request.user or request.user.is_staff:
        patrouille.delete()
        messages.success(request, "La patrouille a été annulée.")
    return redirect('planning')