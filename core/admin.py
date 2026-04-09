from django.contrib import admin
from .models import Actualite, Materiel, RisqueIncendie, Candidature

admin.site.register(Actualite)
admin.site.register(Materiel)
admin.site.register(RisqueIncendie)
admin.site.register(Candidature)