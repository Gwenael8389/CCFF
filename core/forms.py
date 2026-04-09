from django import forms
from .models import Actualite, PhotoGalerie

class ActualiteForm(forms.ModelForm):
    class Meta:
        model = Actualite
        fields = ['titre', 'contenu', 'image']
        widgets = {
            'titre': forms.TextInput(attrs={'class': 'w-full bg-slate-50 border border-slate-200 rounded-xl px-4 py-3 focus:ring-2 focus:ring-brand-500 font-bold'}),
            'contenu': forms.Textarea(attrs={'class': 'w-full bg-slate-50 border border-slate-200 rounded-xl px-4 py-3 focus:ring-2 focus:ring-brand-500', 'rows': 5}),
        }

class PhotoForm(forms.ModelForm):
    class Meta:
        model = PhotoGalerie
        fields = ['titre', 'image']
        widgets = {
            'titre': forms.TextInput(attrs={'class': 'w-full bg-slate-50 border border-slate-200 rounded-xl px-4 py-3 focus:ring-2 focus:ring-brand-500 font-bold'}),
        }