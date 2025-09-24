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
        fields = ['kundenauftrag','kundenname', 'statuskundenauftrag','v_endtermin'] # 25.06.2025: status_kundenauftrag dazu gefügt
        widgets = {
            "kundenname": KundeWidget(attrs={"data-placeholder": "Kunden suchen", "style": "width: 300px;"}),
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
        fields=['id', 'bezeichnung', 'k_auftragsmenge', 'k_fertigungsauftrag', 'k_endtermin', 'statuskomponente']

class MerkmaleForm(forms.ModelForm):
    materialnummer = forms.ModelChoiceField(
        queryset=Material.objects.all(),
        widget=ModelSelect2Widget(
            model=Material,
            search_fields=['materialnummer__icontains', 'bezeichnung__icontains'],
            attrs={
                'data-placeholder': 'Material auswählen',
                'style': 'width:100%;'
            }
        ),
        label="Materialnummer"
    )

    class Meta:
        model = Merkmale
        fields = ['materialnummer', 'm_durchmesser', 'm_gewicht']


class UrblattForm(forms.ModelForm):
    materialnummer = forms.ModelChoiceField(
        queryset=Material.objects.all(),
        widget=ModelSelect2Widget(
            model=Material,
            search_fields=['materialnummer__icontains', 'bezeichnung__icontains'],
            attrs={
                'data-placeholder': 'Material auswählen',
                'style': 'width:100%;'
            }
        ),
        label="Materialnummer"
    )

    class Meta:
        model = Urblatt
        fields = ['materialnummer', 'u_schnittwerkzeug',"u_bild"]

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
        fields = ['kundenauftrag','bezeichnung','p_auftragsmenge','p_fertigungsauftrag','p_endtermin', 'statusprodukt']
        widgets = {
            "bezeichnung": MaterialWidget(attrs={
                "data-placeholder": "Material suchen",
                "style": "width: 450px;"  # Breite des Feldes
            }),
            "materialnummer": forms.TextInput(attrs={"readonly": "readonly"}),
        }

Kd_formset = inlineformset_factory(
    Kundenauftrag, 
    Produkt,
    form=ProduktForm, 
    can_delete = False, 
    extra=1,max_num=8, 
    fields=['id','kundenauftrag','bezeichnung','p_auftragsmenge','p_fertigungsauftrag','p_endtermin', 'statusprodukt'],

)
Prod_formset = inlineformset_factory(
    Produkt,
    Komponente,
    form=ProduktForm, 
    can_delete=False,
    extra=1,
    max_num=8,
    fields=['id','product','bezeichnung','k_auftragsmenge','k_fertigungsauftrag','k_endtermin', 'statuskomponente'],

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