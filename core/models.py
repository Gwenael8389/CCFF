from django.db import models
from django.contrib.auth.models import User

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

    def __str__(self):
        return f"Candidature de {self.prenom} {self.nom}"
    
class MessageContact(models.Model):
    nom = models.CharField(max_length=100)
    email = models.EmailField()
    sujet = models.CharField(max_length=200)
    message = models.TextField()
    date_envoi = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message de {self.nom} - {self.sujet}"
    
class PhotoGalerie(models.Model):
    titre = models.CharField(max_length=100, help_text="Ex: Formation avec le SDIS")
    image = models.ImageField(upload_to='galerie/')
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
    fichier = models.FileField(upload_to='intranet_docs/')
    categorie = models.CharField(max_length=20, choices=CATEGORIES, default='AUTRE')
    date_ajout = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"[{self.get_categorie_display()}] {self.titre}"