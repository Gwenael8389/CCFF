from django import forms
from .models import Actualite, PhotoGalerie, DossierGalerie

class ActualiteForm(forms.ModelForm):
    class Meta:
        model = Actualite
        fields = ['titre', 'contenu', 'image']
        widgets = {
            'titre': forms.TextInput(attrs={'class': 'w-full bg-slate-50 border border-slate-200 rounded-xl px-4 py-3 focus:ring-2 focus:ring-brand-500 font-bold'}),
            # L'ID 'tinymce-editor' est crucial ici pour activer l'éditeur style Word
            'contenu': forms.Textarea(attrs={'id': 'tinymce-editor', 'class': 'w-full'}),
        }

class PhotoForm(forms.ModelForm):
    # Champ virtuel qui n'est pas dans la base de données, juste pour le formulaire
    nouveau_dossier = forms.CharField(
        max_length=100, 
        required=False, 
        widget=forms.TextInput(attrs={'class': 'w-full bg-slate-50 border border-slate-200 rounded-xl px-4 py-3 focus:ring-2 focus:ring-blue-500', 'placeholder': 'Ou tapez le nom d\'un NOUVEAU dossier...'})
    )

    class Meta:
        model = PhotoGalerie
        fields = ['dossier', 'nouveau_dossier', 'titre', 'image']
        widgets = {
            'dossier': forms.Select(attrs={'class': 'w-full bg-slate-50 border border-slate-200 rounded-xl px-4 py-3 focus:ring-2 focus:ring-blue-500 text-slate-700 font-bold'}),
            'titre': forms.TextInput(attrs={'class': 'w-full bg-slate-50 border border-slate-200 rounded-xl px-4 py-3 focus:ring-2 focus:ring-blue-500 font-bold', 'placeholder': 'Légende (Optionnelle)'}),
        }