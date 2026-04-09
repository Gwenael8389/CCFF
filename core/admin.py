from django.contrib import admin
from .models import (Actualite, Materiel, RisqueIncendie, Candidature, 
                     MessageContact, PhotoGalerie, MembreEquipe, DocumentIntranet, 
                     Patrouille, SignalementMateriel, Alerte, AbonneNewsletter, 
                     ArticleEPI, Dotation, DossierGalerie)

admin.site.register(Actualite)
admin.site.register(Materiel)
admin.site.register(RisqueIncendie)
admin.site.register(Candidature)
admin.site.register(MessageContact)
admin.site.register(PhotoGalerie)
admin.site.register(MembreEquipe)
admin.site.register(DocumentIntranet)
admin.site.register(Patrouille)
admin.site.register(SignalementMateriel)
admin.site.register(Alerte)
admin.site.register(AbonneNewsletter)
admin.site.register(ArticleEPI)
admin.site.register(Dotation)
admin.site.register(DossierGalerie)