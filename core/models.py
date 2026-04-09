from django.db import models
from django.contrib.auth.models import User
from django.db.models import Q
from cloudinary_storage.storage import RawMediaCloudinaryStorage

class Actualite(models.Model):
    titre = models.CharField(max_length=200)
    contenu = models.TextField()
    image = models.ImageField(upload_to='actus/', blank=True, null=True)
    date_publication = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.titre

class Materiel(models.Model):
    CATEGORIES = [
        ('VEHICULE', 'Véhicule'),
        ('RADIO', 'Radio'),
        ('OUTIL', 'Outil / Pompe'),
    ]
    nom = models.CharField(max_length=100)
    categorie = models.CharField(max_length=20, choices=CATEGORIES)
    en_service = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.nom} ({self.get_categorie_display()})"
    
class RisqueIncendie(models.Model):
    NIVEAUX = [
        ('JAUNE', 'Modéré (Jaune)'),
        ('ORANGE', 'Sévère (Orange)'),
        ('ROUGE', 'Très Sévère (Rouge)'),
        ('NOIR', 'Extrême (Noir)'),
    ]
    niveau = models.CharField(max_length=10, choices=NIVEAUX, default='ORANGE')
    date_mise_a_jour = models.DateTimeField(auto_now=True)

    @property
    def style_couleur(self):
        if self.niveau == 'JAUNE': return 'bg-yellow-400 text-slate-900'
        if self.niveau == 'ORANGE': return 'bg-orange-500 text-white'
        if self.niveau == 'ROUGE': return 'bg-red-600 text-white'
        if self.niveau == 'NOIR': return 'bg-black text-white'
        return 'bg-slate-200 text-slate-800'

    def __str__(self):
        return f"Risque actuel : {self.get_niveau_display()}"

class Candidature(models.Model):
    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    email = models.EmailField()
    telephone = models.CharField(max_length=20)
    message = models.TextField()
    date_candidature = models.DateTimeField(auto_now_add=True)
    est_traite = models.BooleanField(default=False, help_text="Cocher quand la candidature a été traitée")

    def __str__(self):
        return f"Candidature de {self.prenom} {self.nom}"
    
class MessageContact(models.Model):
    nom = models.CharField(max_length=100)
    email = models.EmailField()
    sujet = models.CharField(max_length=200)
    message = models.TextField()
    date_envoi = models.DateTimeField(auto_now_add=True)
    est_traite = models.BooleanField(default=False, help_text="Cocher quand une réponse a été apportée")

    def __str__(self):
        return f"Message de {self.nom} - {self.sujet}"
    
class DossierGalerie(models.Model):
    nom = models.CharField(max_length=100, unique=True, help_text="Nom du dossier (ex: Formation SDIS 2024)")
    date_creation = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Dossier Galerie"
        verbose_name_plural = "Dossiers Galerie"
        ordering = ['-date_creation']

    def __str__(self):
        return self.nom

class PhotoGalerie(models.Model):
    titre = models.CharField(max_length=100, help_text="Légende de la photo")
    image = models.ImageField(upload_to='galerie/')
    dossier = models.ForeignKey(DossierGalerie, on_delete=models.SET_NULL, null=True, blank=True, related_name='photos')
    date_ajout = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.titre

class MembreEquipe(models.Model):
    nom = models.CharField(max_length=100, help_text="Prénom et Nom")
    role = models.CharField(max_length=100, help_text="Ex: Président, Chef d'équipe...")
    photo = models.ImageField(upload_to='equipe/', blank=True, null=True)
    ordre = models.IntegerField(default=0, help_text="Mettre 1 pour le président, 2 pour le vice-président, etc.")

    class Meta:
        ordering = ['ordre', 'nom']

    def __str__(self):
        return f"{self.nom} - {self.role}"

class DocumentIntranet(models.Model):
    CATEGORIES = [
        ('FORMATION', 'Manuel & Formation'),
        ('PLAN', 'Plan de Patrouille & Cartes'),
        ('CR', 'Compte-Rendu de Réunion'),
        ('AUTRE', 'Autre Document'),
    ]
    titre = models.CharField(max_length=200)
    fichier = models.FileField(upload_to='intranet_docs/', storage=RawMediaCloudinaryStorage())
    categorie = models.CharField(max_length=20, choices=CATEGORIES, default='AUTRE')
    date_ajout = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"[{self.get_categorie_display()}] {self.titre}"
    
class Patrouille(models.Model):
    TYPES = [
        ('MOBILE', 'Patrouille Mobile (4x4)'),
        ('VIGIE', 'Point de Vigie'),
    ]
    MISSION_CHOICES = [
        ('CCFF', 'Mission CCFF (Communale)'),
        ('RCSC', 'Mission RCSC (Réserve Civile)'),
    ]
    METEO_CHOICES = [
        ('NORMAL', 'Temps calme / Dégagé'),
        ('VENT', 'Mistral / Vent fort'),
        ('CANICULE', 'Forte chaleur'),
        ('ORAGE', 'Risque Orageux'),
    ]

    date_patrouille = models.DateField()
    heure_debut = models.TimeField()
    heure_fin = models.TimeField()
    type_patrouille = models.CharField(max_length=20, choices=TYPES, default='MOBILE')
    
    chef_de_bord = models.ForeignKey(User, on_delete=models.CASCADE, related_name='patrouilles_dirigees')
    coequipier = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='patrouilles_assistees')
    vehicule = models.ForeignKey(Materiel, on_delete=models.SET_NULL, null=True, blank=True, limit_choices_to={'categorie': 'VEHICULE'})
    
    # NOUVEAU : Type de mission
    mission_type = models.CharField(max_length=10, choices=MISSION_CHOICES, default='CCFF')

    # NOUVEAU : Checklist de départ
    chk_huile = models.BooleanField(default=False, verbose_name="Niveau d'huile")
    chk_eau = models.BooleanField(default=False, verbose_name="Niveau d'eau / LDR")
    chk_carburant = models.BooleanField(default=False, verbose_name="Plein de carburant")
    chk_radio = models.BooleanField(default=False, verbose_name="Essai Radio VHF")
    chk_pneus = models.BooleanField(default=False, verbose_name="État des pneus")
    chk_pompe = models.BooleanField(default=False, verbose_name="Test motopompe / Eau cuve")

    # Données de fin
    meteo = models.CharField(max_length=50, choices=METEO_CHOICES, blank=True, null=True)
    km_debut = models.PositiveIntegerField(blank=True, null=True)
    km_fin = models.PositiveIntegerField(blank=True, null=True)
    rapport = models.TextField(blank=True, null=True, help_text="Main courante / incidents")
    est_terminee = models.BooleanField(default=False)

    # NOUVEAU : Signatures numériques (Texte long pour l'image Base64)
    signature_chef = models.TextField(blank=True, null=True)
    signature_coequipier = models.TextField(blank=True, null=True)
    
    # À ajouter dans la classe Patrouille
    rapport_pdf = models.FileField(upload_to='rapports_pdf/', blank=True, null=True, storage=RawMediaCloudinaryStorage())
    
    class Meta:
        ordering = ['date_patrouille', 'heure_debut']

    def __str__(self):
        return f"{self.get_type_patrouille_display()} du {self.date_patrouille.strftime('%d/%m/%Y')} - Chef: {self.chef_de_bord.username}"

class Alerte(models.Model):
    titre = models.CharField(max_length=100, help_text="Ex: DEPART DE FEU - MASSIF NORD")
    message = models.TextField(help_text="Instructions pour les bénévoles")
    est_active = models.BooleanField(default=True)
    date_lancement = models.DateTimeField(auto_now_add=True)
    auteur = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f"[{'ACTIVE' if self.est_active else 'FIN'}] {self.titre}"
    
class AbonneNewsletter(models.Model):
    email = models.EmailField(unique=True, help_text="Adresse email de l'habitant")
    date_inscription = models.DateTimeField(auto_now_add=True)
    est_actif = models.BooleanField(default=True, help_text="Abonné aux alertes et newsletters")

    class Meta:
        verbose_name = "Abonné Newsletter"
        verbose_name_plural = "Abonnés Newsletter"

    def __str__(self):
        return self.email

class SignalementMateriel(models.Model):
    materiel = models.ForeignKey(Materiel, on_delete=models.CASCADE, related_name='signalements')
    signale_par = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    description = models.TextField(help_text="Décrivez le problème (ex: Pneu crevé, radio grésille...)")
    date_signalement = models.DateTimeField(auto_now_add=True)
    est_resolu = models.BooleanField(default=False)
    date_resolution = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ['-date_signalement']
        verbose_name = "Signalement Matériel"
        verbose_name_plural = "Signalements Matériel"

    def __str__(self):
        statut = "RÉSOLU" if self.est_resolu else "EN COURS"
        return f"[{statut}] {self.materiel.nom} - {self.date_signalement.strftime('%d/%m/%Y')}"
    
class ArticleEPI(models.Model):
    CATEGORIES = [
        ('VETEMENT', 'Vêtement (Veste, Pantalon, Polo)'),
        ('CHAUSSURE', 'Chaussures / Rangers'),
        ('EPI', 'Équipement (Casque, Gants, Lampe)'),
    ]
    nom = models.CharField(max_length=100, help_text="Ex: Veste F1, Pantalon, Rangers...")
    categorie = models.CharField(max_length=20, choices=CATEGORIES, default='VETEMENT')
    prix_indicatif = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True, help_text="Pour estimer la valeur du vestiaire")

    class Meta:
        verbose_name = "Article EPI"
        verbose_name_plural = "Articles EPI"
        ordering = ['categorie', 'nom']

    def __str__(self):
        return self.nom

class Dotation(models.Model):
    ETAT_CHOICES = [
        ('NEUF', 'Neuf'),
        ('BON', 'Bon état'),
        ('USE', 'Usé / À remplacer'),
    ]
    benevole = models.ForeignKey(User, on_delete=models.CASCADE, related_name='dotations')
    article = models.ForeignKey(ArticleEPI, on_delete=models.CASCADE)
    taille = models.CharField(max_length=20, help_text="Ex: M, XL, 42, 44...")
    date_remise = models.DateField(auto_now_add=True)
    etat_actuel = models.CharField(max_length=10, choices=ETAT_CHOICES, default='NEUF')
    est_rendu = models.BooleanField(default=False, help_text="Cocher quand le bénévole rend le matériel")

    class Meta:
        verbose_name = "Dotation Bénévole"
        verbose_name_plural = "Dotations Bénévoles"
        ordering = ['benevole__first_name', '-date_remise']

    def __str__(self):
        statut = "RENDU" if self.est_rendu else "EN POSSESSION"
        return f"[{statut}] {self.article.nom} ({self.taille}) - {self.benevole.username}"