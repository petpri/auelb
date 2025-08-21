from django import forms
from django.forms import inlineformset_factory
from .models import Kundenauftrag, Produkt, Komponente, StatusKundenauftrag, StatusProdukt, StatusKomponente,Kunde,Material
from django_select2 import forms as s2forms
from django_select2.forms import ModelSelect2Widget




class AuthorWidget(s2forms.ModelSelect2Widget):
    search_fields = [
        "kundenname__icontains",
    ]

class ProduktWidget(s2forms.ModelSelect2Widget):
    search_fields = [
        "bezeichnung__icontains",
    ]

class KundenauftragForm(forms.ModelForm):
    class Meta:
        model = Kundenauftrag
        fields = ['kundenauftrag','kundenname', 'statuskundenauftrag'] # 25.06.2025: status_kundenauftrag dazu gefügt
        widgets = {
            "kundenname": AuthorWidget,
        }

class KundeForm(forms.ModelForm):
    class Meta:
        model = Kunde
        fields = ['id','kundennummer', 'kundenname'] 


class MaterialForm(forms.ModelForm):
    class Meta:
        model = Material
        fields = ['id','materialnummer', 'bezeichnung']
 
    
class KomponenteForm(forms.ModelForm):
    class Meta:
        model = Komponente
        fields=['id', 'bezeichnung', 'k_auftragsmenge', 'k_fertigungsauftrag', 'k_endtermin', 'statuskomponente']

class ProduktForm(forms.ModelForm):
    class Meta:
        model = Produkt
        fields=['kundenauftrag','bezeichnung','p_auftragsmenge','p_fertigungsauftrag','p_endtermin', 'statusprodukt']
        widgets = {
            "bezeichnung": ModelSelect2Widget(
                model=Material,
                search_fields=["bezeichnung__icontains"],
                attrs={"data-placeholder": "Material suchen"}
            ),
            "materialnummer": forms.TextInput(attrs={"readonly": "readonly"}),
        }

Kd_formset = inlineformset_factory(Kundenauftrag, Produkt,form=ProduktForm, can_delete = False, extra=1,max_num=8, fields=['id','kundenauftrag','bezeichnung','p_auftragsmenge','p_fertigungsauftrag','p_endtermin', 'statusprodukt'],
        widgets = {
            "bezeichnung": ModelSelect2Widget(
                model=Material,
                search_fields=["bezeichnung__icontains"],
                attrs={"data-placeholder": "Material suchen", "style": "width: 300px;" }
            ),
            "materialnummer": forms.TextInput(attrs={"readonly": "readonly"}),
        })
Prod_formset = inlineformset_factory(Produkt, Komponente, can_delete = False, extra=1,max_num=8,  fields=['id','product','bezeichnung','k_auftragsmenge','k_fertigungsauftrag','k_endtermin', 'statuskomponente'],
        widgets = {
            "bezeichnung": ModelSelect2Widget(
                model=Material,
                search_fields=["bezeichnung__icontains"],
                attrs={"data-placeholder": "Material suchen", "style": "width: 300px;" }
            ),
            "materialnummer": forms.TextInput(attrs={"readonly": "readonly"}),
        })


class AuswahlForm_KD(forms.Form):
    #queryset=StatusKundenauftrag.objects.all()
    #auswahl = forms.ModelChoiceField(queryset, to_field_name='kd_auswahl')
    class Meta:
        model = StatusKundenauftrag
        fields = ['kd_auswahl']

class AuswahlForm_PROD(forms.Form):
    #queryset=StatusKundenauftrag.objects.all()
    #auswahl = forms.ModelChoiceField(queryset, to_field_name='kd_auswahl')
    class Meta:
        model = StatusProdukt
        fields = ['produkt_auswahl']

class AuswahlForm_KOMP(forms.Form):
    #queryset=StatusKundenauftrag.objects.all()
    #auswahl = forms.ModelChoiceField(queryset, to_field_name='kd_auswahl')
    class Meta:
        model = StatusKomponente
        fields = ['komponente_auswahl']