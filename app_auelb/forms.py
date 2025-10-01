from django import forms
from django.forms import inlineformset_factory
from .models import Kundenauftrag, Produkt, Komponente, StatusKundenauftrag, StatusProdukt, StatusKomponente,Kunde,Material,Merkmale,Urblatt
from django_select2 import forms as s2forms
from django_select2.forms import ModelSelect2Widget




#class AuthorWidget(s2forms.ModelSelect2Widget):
#    model = Kunde
#    search_fields = [
#        "kundenname__icontains",
#    ]
#    attrs = {"data-placeholder": "Kunden suchen", "style": "width: 300px;"}

#class ProduktWidget(s2forms.ModelSelect2Widget):
#    search_fields = [
#        "bezeichnung__icontains",
#    ]

class KundeWidget(ModelSelect2Widget):
    model = Kunde
    search_fields = [
        "kundenname__icontains",
        "kundennummer__icontains",
    ]

    def get_result_label(self, item):
        return f"{item.kundenname} ({item.kundennummer})"

    def get_selected_result_label(self, item):
        return f"{item.kundenname}"



class KundenauftragForm(forms.ModelForm):
    class Meta:
        model = Kundenauftrag
        fields = ['kundenauftrag','kundenname', 'statuskundenauftrag','v_endtermin','kun_infofeld'] # 25.06.2025: status_kundenauftrag dazu gefügt
        widgets = {
            "kundenname": KundeWidget(attrs={"data-placeholder": "Kunden suchen", "style": "width: 300px;"}),
            "kun_infofeld": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 1,  # <-- Höhe wie ein normales Input-Feld
                "style": "resize:none;"  # optional: verhindert das manuelle Vergrößern
            }),
        }

#class KundeForm(forms.ModelForm):
#    class Meta:
#        model = Kunde
#        fields = ['id','kundennummer', 'kundenname']


class MaterialForm(forms.ModelForm):
    class Meta:
        model = Material
        fields = ['id','materialnummer', 'bezeichnung']


class KomponenteForm(forms.ModelForm):
    class Meta:
        model = Komponente
        fields=['id', 'bezeichnung', 'k_auftragsmenge', 'k_fertigungsauftrag', 'k_endtermin','k_infofeld', 'statuskomponente']

class MerkmaleForm(forms.ModelForm):
    class Meta:
        model = Merkmale
        fields = ['m_bild']  # nur das Bildfeld, Materialnummer wird nicht als Eingabefeld angezeigt
        widgets = {
            'm_bild': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            "k_infofeld": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 1,  # <-- Höhe wie ein normales Input-Feld
                "style": "resize:none;"  # optional: verhindert das manuelle Vergrößern
            }),
        }

class UrblattForm(forms.ModelForm):
    class Meta:
        model = Urblatt
        fields = ['u_bild']  # nur das Bildfeld
        widgets = {
            'u_bild': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }

class MaterialWidget(ModelSelect2Widget):
    model = Material
    search_fields = ["bezeichnung__icontains", "materialnummer__icontains" ]


    # Wird in der Dropdown-Suche angezeigt
    def get_result_label(self, item):
        return f"{item.bezeichnung} ({item.materialnummer})"

    # Nach Auswahl im Inputfeld (optional nur Bezeichnung)
    def get_selected_result_label(self, item):
        return f"{item.bezeichnung}"




class ProduktForm(forms.ModelForm):
    class Meta:
        model = Produkt
        fields = ['kundenauftrag','bezeichnung','p_auftragsmenge','p_fertigungsauftrag','p_endtermin', 'statusprodukt','p_infofeld']
        widgets = {
            "bezeichnung": MaterialWidget(attrs={
                "data-placeholder": "Material suchen",
                "style": "width: 450px;"  # Breite des Feldes
            }),
            "materialnummer": forms.TextInput(attrs={"readonly": "readonly"}),
            "p_infofeld": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 1,  # <-- Höhe wie ein normales Input-Feld
                "style": "resize:none;"  # optional: verhindert das manuelle Vergrößern
            }),
        }

Kd_formset = inlineformset_factory(
    Kundenauftrag,
    Produkt,
    form=ProduktForm,
    can_delete = False,
    extra=1,max_num=8,
    fields=['id','kundenauftrag','bezeichnung','p_auftragsmenge','p_fertigungsauftrag','p_endtermin','p_infofeld', 'statusprodukt'],

)
Prod_formset = inlineformset_factory(
    Produkt,
    Komponente,
    form=ProduktForm,
    can_delete=False,
    extra=1,
    max_num=8,
    fields=['id','product','bezeichnung','k_auftragsmenge','k_fertigungsauftrag','k_endtermin','k_infofeld', 'statuskomponente'],

)


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