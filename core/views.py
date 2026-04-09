from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib import messages
from .models import Actualite, Materiel, RisqueIncendie, Candidature, MessageContact, PhotoGalerie, MembreEquipe, DocumentIntranet, Patrouille, Alerte, AbonneNewsletter, SignalementMateriel
from django.contrib.auth.decorators import login_required,user_passes_test
from datetime import date, datetime, timedelta
from django.utils import timezone
from django.db.models import Q
import calendar
from django.core.mail import send_mail
from django.conf import settings
from django.http import HttpResponseRedirect
from .forms import ActualiteForm, PhotoForm

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

def calculer_duree_totale(patrouilles):
    total_secondes = 0
    for p in patrouilles:
        if p.heure_debut and p.heure_fin:
            # On combine avec la date du jour juste pour faire le calcul mathématique
            debut = datetime.combine(date.today(), p.heure_debut)
            fin = datetime.combine(date.today(), p.heure_fin)
            if fin < debut: # Si la patrouille a croisé minuit
                fin += timedelta(days=1)
            
            # On calcule la durée de la patrouille
            duree_patrouille = (fin - debut).total_seconds()
            
            # Si on veut les heures-bénévoles (2 personnes dans la voiture = 2x plus d'heures)
            multiplicateur = 2 if p.coequipier else 1
            total_secondes += (duree_patrouille * multiplicateur)
            
    heures = int(total_secondes // 3600)
    return heures

@login_required(login_url='/connexion/')
def intranet(request):
    user = request.user
    annee_en_cours = date.today().year

    # Patrouilles globales terminées cette année
    patrouilles_terminees_annee = Patrouille.objects.filter(est_terminee=True, date_patrouille__year=annee_en_cours)
    
    # 1. Stats personnelles
    mes_patrouilles = Patrouille.objects.filter(Q(chef_de_bord=user) | Q(coequipier=user), date_patrouille__year=annee_en_cours)
    nb_mes_patrouilles = mes_patrouilles.count()
    mes_heures = calculer_duree_totale(mes_patrouilles.filter(est_terminee=True)) # APPEL DE LA FONCTION

    # 2. Stats globales
    total_patrouilles_ccff = Patrouille.objects.filter(date_patrouille__year=annee_en_cours).count()
    heures_globales_ccff = calculer_duree_totale(patrouilles_terminees_annee) # APPEL DE LA FONCTION

    prochaine_patrouille = Patrouille.objects.filter(Q(chef_de_bord=user) | Q(coequipier=user), date_patrouille__gte=date.today()).order_by('date_patrouille').first()
    documents = DocumentIntranet.objects.all().order_by('-date_ajout')
    alerte_active = Alerte.objects.filter(est_active=True).first()
    rapports_en_attente = Patrouille.objects.filter(chef_de_bord=user, est_terminee=False, date_patrouille__lte=date.today()).order_by('date_patrouille')

    context = {
        'nb_mes_patrouilles': nb_mes_patrouilles,
        'mes_heures': mes_heures, # NOUVEAU
        'total_patrouilles_ccff': total_patrouilles_ccff,
        'heures_globales_ccff': heures_globales_ccff, # NOUVEAU
        'prochaine_patrouille': prochaine_patrouille,
        'documents': documents,
        'annee_en_cours': annee_en_cours,
        'alerte_active': alerte_active,
        'rapports_en_attente': rapports_en_attente,
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
    patrouille = get_object_or_404(Patrouille, id=patrouille_id)
    
    # CORRECTION DU SYSTÈME D'INSCRIPTION COÉQUIPIER
    if patrouille.coequipier == request.user:
        patrouille.coequipier = None
        patrouille.save()
        messages.success(request, "Vous vous êtes désinscrit de cette patrouille.")
    elif patrouille.coequipier is None and patrouille.chef_de_bord != request.user:
        patrouille.coequipier = request.user
        patrouille.save()
        messages.success(request, "Vous êtes inscrit comme coéquipier !")
    else:
        messages.error(request, "Impossible de modifier cette inscription.")
        
    return redirect('planning')

@login_required(login_url='/connexion/')
def supprimer_patrouille(request, patrouille_id):
    patrouille = get_object_or_404(Patrouille, id=patrouille_id)
    if patrouille.chef_de_bord == request.user or request.user.is_staff:
        patrouille.delete()
        messages.success(request, "La patrouille a été annulée.")
    return redirect('planning')

@login_required(login_url='/connexion/')
def saisir_rapport(request, patrouille_id):
    patrouille = get_object_or_404(Patrouille, id=patrouille_id, chef_de_bord=request.user)

    if request.method == 'POST':
        phase = request.POST.get('phase')
        
        # --- PHASE 1 : LE DÉPART ---
        if phase == 'depart':
            patrouille.mission_type = request.POST.get('mission_type')
            patrouille.km_debut = request.POST.get('km_debut')
            patrouille.chk_huile = request.POST.get('chk_huile') == 'on'
            patrouille.chk_eau = request.POST.get('chk_eau') == 'on'
            patrouille.chk_carburant = request.POST.get('chk_carburant') == 'on'
            patrouille.chk_radio = request.POST.get('chk_radio') == 'on'
            patrouille.chk_pneus = request.POST.get('chk_pneus') == 'on'
            patrouille.chk_pompe = request.POST.get('chk_pompe') == 'on'
            patrouille.save()
            messages.success(request, "Checklist validée. Bonne patrouille !")
            
        # --- PHASE 2 : LE RETOUR ---
        elif phase == 'retour':
            patrouille.km_fin = request.POST.get('km_fin')
            patrouille.meteo = request.POST.get('meteo')
            patrouille.rapport = request.POST.get('rapport')
            patrouille.signature_chef = request.POST.get('signature_chef')
            patrouille.signature_coequipier = request.POST.get('signature_coequipier')
            patrouille.est_terminee = True
            patrouille.save()
            messages.success(request, "Patrouille clôturée et rapport signé avec succès !")
            
        return redirect('intranet')

    return render(request, 'rapport.html', {'patrouille': patrouille})

@login_required(login_url='/connexion/')
def gestion_alerte(request):
    # Seul le staff (bureau/président) peut gérer les alertes
    if not request.user.is_staff:
        return redirect('intranet')

    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'lancer':
            titre = request.POST.get('titre')
            message = request.POST.get('message')
            
            # 1. On crée l'alerte en base de données
            nouvelle_alerte = Alerte.objects.create(titre=titre, message=message, auteur=request.user)
            
            # 2. On envoie un email à tous les bénévoles actifs
            emails_benevoles = list(User.objects.filter(is_active=True).values_list('email', flat=True))
            emails_valides = [email for email in emails_benevoles if email] # On retire les champs vides
            
            if emails_valides:
                send_mail(
                    subject=f"🚨 ALERTE CCFF: {titre}",
                    message=f"Alerte déclenchée par {request.user.first_name}.\n\nMessage : {message}\n\nConnectez-vous sur l'intranet pour plus d'infos.",
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=emails_valides,
                    fail_silently=True, # Si l'email échoue (pas de SMTP configuré), ça ne fait pas planter le site
                )
            
            messages.success(request, "Alerte générale déclenchée et emails envoyés !")
            
        elif action == 'stopper':
            Alerte.objects.filter(est_active=True).update(est_active=False)
            messages.success(request, "L'alerte a été désactivée.")
            
        return redirect('intranet')
        
    return render(request, 'alerte.html')

# On garde uniquement cette vue pour les archives
@user_passes_test(lambda u: u.is_superuser, login_url='/intranet/')
def archives_rapports(request):
    rapports = Patrouille.objects.filter(est_terminee=True).order_by('-date_patrouille')
    return render(request, 'archives.html', {'rapports': rapports})

# On remplace la génération PDF par une simple vue de consultation
@user_passes_test(lambda u: u.is_superuser, login_url='/intranet/')
def voir_rapport(request, patrouille_id):
    patrouille = get_object_or_404(Patrouille, id=patrouille_id, est_terminee=True)
    return render(request, 'voir_rapport.html', {'patrouille': patrouille})

def inscription_newsletter(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        if email:
            # On vérifie si la personne n'est pas déjà inscrite pour éviter les doublons
            if AbonneNewsletter.objects.filter(email=email).exists():
                messages.info(request, "Cette adresse e-mail est déjà inscrite à nos alertes. Merci !")
            else:
                AbonneNewsletter.objects.create(email=email)
                messages.success(request, "Merci ! Vous êtes maintenant inscrit aux alertes citoyennes de Besse-sur-Issole.")
    
    # Redirige l'utilisateur vers la page d'où il vient (ou l'accueil par défaut)
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

@login_required(login_url='/connexion/')
def gestion_materiel(request):
    if request.method == 'POST':
        action = request.POST.get('action')
        
        # Le bénévole signale une panne
        if action == 'signaler':
            materiel_id = request.POST.get('materiel')
            description = request.POST.get('description')
            materiel = get_object_or_404(Materiel, id=materiel_id)
            
            SignalementMateriel.objects.create(
                materiel=materiel,
                signale_par=request.user,
                description=description
            )
            messages.success(request, "Incident signalé avec succès. L'équipe logistique est prévenue !")
            
        # Un administrateur marque la panne comme résolue
        elif action == 'resoudre' and request.user.is_staff:
            signalement_id = request.POST.get('signalement_id')
            signalement = get_object_or_404(SignalementMateriel, id=signalement_id)
            signalement.est_resolu = True
            signalement.date_resolution = timezone.now()
            signalement.save()
            messages.success(request, f"L'incident sur {signalement.materiel.nom} a été marqué comme résolu.")
            
        return redirect('gestion_materiel')
    
    # Affichage de la page
    materiels = Materiel.objects.filter(en_service=True).order_by('categorie', 'nom')
    incidents_en_cours = SignalementMateriel.objects.filter(est_resolu=False)
    incidents_resolus = SignalementMateriel.objects.filter(est_resolu=True)[:5] # Les 5 derniers résolus
    
    return render(request, 'materiel.html', {
        'materiels': materiels,
        'incidents_en_cours': incidents_en_cours,
        'incidents_resolus': incidents_resolus
    })

@login_required(login_url='/connexion/')
def publier_contenu(request):
    if not request.user.is_staff:
        messages.error(request, "Accès réservé au bureau.")
        return redirect('intranet')

    form_actu = ActualiteForm()
    form_photo = PhotoForm()

    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'actualite':
            form_actu = ActualiteForm(request.POST, request.FILES)
            if form_actu.is_valid():
                form_actu.save()
                messages.success(request, "Actualité publiée !")
                return redirect('actualites')
                
        elif action == 'photo':
            form_photo = PhotoForm(request.POST, request.FILES)
            if form_photo.is_valid():
                form_photo.save()
                messages.success(request, "Photo ajoutée à la galerie !")
                return redirect('galerie')

    return render(request, 'publier.html', {'form_actu': form_actu, 'form_photo': form_photo})