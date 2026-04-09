from django.db import models
from django.contrib.auth.models import User

class Actualite(models.Model):
    titre = models.CharField(max_length=200)
    contenu = models.TextField()
    image = models.ImageField(upload_to='actus/', blank=True, null=True)
    date_publication = models.DateTimeField(auto_now_add=True)

    # Correction ici : c'est __str__ et non __claire__
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