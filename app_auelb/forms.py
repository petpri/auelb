from django import forms
from django.forms import inlineformset_factory
from django_select2.forms import ModelSelect2Widget
from .models import (
    Kundenauftrag, Produkt, Komponente, StatusKundenauftrag, 
    StatusProdukt, StatusKomponente, Kunde, Material, Merkmale, Urblatt
)

# -------------------------
# Select2 Widgets
# -------------------------
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

class MaterialWidget(ModelSelect2Widget):
    model = Material
    search_fields = ["bezeichnung__icontains", "materialnummer__icontains"]

    def get_result_label(self, item):
        return f"{item.bezeichnung} ({item.materialnummer})"

    def get_selected_result_label(self, item):
        return f"{item.bezeichnung}"


# -------------------------
# Kundenauftrag Form
# -------------------------
class KundenauftragForm(forms.ModelForm):
    class Meta:
        model = Kundenauftrag
        fields = ['kundenauftrag', 'kundenname', 'statuskundenauftrag', 'v_endtermin', 'kun_infofeld']
        widgets = {
            "kundenname": KundeWidget(attrs={"data-placeholder": "Kunden suchen", "style": "width: 300px;"}),
            "kun_infofeld": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 1,
                "style": "resize:none;"
            }),
        }


# -------------------------
# Material Form
# -------------------------
class MaterialForm(forms.ModelForm):
    class Meta:
        model = Material
        fields = ['materialnummer', 'bezeichnung']


# -------------------------
# Komponente Form
# -------------------------
class KomponenteForm(forms.ModelForm):
    class Meta:
        model = Komponente
        fields = [
            'bezeichnung', 'k_auftragsmenge', 'k_fertigungsauftrag', 
            'k_endtermin', 'k_infofeld', 'statuskomponente'
        ]
        widgets = {
            "bezeichnung": MaterialWidget(attrs={
                "data-placeholder": "Material suchen",
                "style": "width: 450px;"
            }),
            "k_infofeld": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 1,
                "style": "resize:none;"
            }),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        self.empty_permitted = True # <-- Hinzugefügt: Leere Formulare zulassen

        # Alle außer PPS_MAWI nur lesbar
        if user and not user.groups.filter(name="PPS_MAWI").exists():
            readonly_fields = ['bezeichnung', 'k_auftragsmenge', 'k_fertigungsauftrag', 'k_endtermin', 'k_infofeld', 'statuskomponente']
            for field in readonly_fields:
                self.fields[field].disabled = True
                self.fields[field].required = False # <-- WICHTIG: Erforderlichkeit entfernen
                # Grau hinterlegt
                existing_class = self.fields[field].widget.attrs.get('class', '')
                self.fields[field].widget.attrs['class'] = (existing_class + ' bg-light text-muted').strip()
                self.fields[field].widget.attrs['style'] = self.fields[field].widget.attrs.get('style', '') + 'background-color:#e9ecef !important;color:#6c757d; !important'



# -------------------------
# Merkmale Form
# -------------------------
class MerkmaleForm(forms.ModelForm):
    class Meta:
        model = Merkmale
        fields = ['m_bild']
        widgets = {
            'm_bild': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }


# -------------------------
# Urblatt Form
# -------------------------
class UrblattForm(forms.ModelForm):
    class Meta:
        model = Urblatt
        fields = ['u_bild']
        widgets = {
            'u_bild': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }


# -------------------------
# Produkt Form mit TVK-Beschränkung
# -------------------------
class ProduktForm(forms.ModelForm):
    class Meta:
        model = Produkt
        fields = [
            'bezeichnung', 'p_auftragsmenge', 'p_fertigungsauftrag',
            'p_endtermin', 'p_endtermin_wunsch', 'p_serviceanfrage', 'p_kalkpreis',
            'p_infofeld', 'statusprodukt'
        ]
        widgets = {
            "bezeichnung": MaterialWidget(attrs={
                "data-placeholder": "Material suchen",
                "style": "width: 450px;"
            }),
            "p_infofeld": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 1,
                "style": "resize:none;"
            }),
        }

    GROUP_READONLY_FIELDS = {
        'TVK': ['p_kalkpreis', 'p_serviceanfrage', 'p_endtermin', 'p_fertigungsauftrag'],
        'Produktion': [
            'kundenauftrag', 'bezeichnung', 'p_auftragsmenge', 'p_fertigungsauftrag',
            'p_endtermin', 'p_endtermin_wunsch', 'p_serviceanfrage', 'p_kalkpreis',
            'p_infofeld', 'statusprodukt'
        ],
    }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        self.empty_permitted = True # <-- Hinzugefügt: Leere Formulare zulassen

        if self.user:
            user_groups = self.user.groups.values_list('name', flat=True)
            for group_name in user_groups:
                readonly_fields = self.GROUP_READONLY_FIELDS.get(group_name, [])
                for field_name in readonly_fields:
                    if field_name in self.fields:
                        field = self.fields[field_name]
                        field.disabled = True  # Setze das Feld auf disabled (readonly)
                        field.required = False # <-- WICHTIG: Erforderlichkeit entfernen
                        
                        # optisches Styling: grau hinterlegt
                        existing_class = field.widget.attrs.get('class', ' ')
                        field.widget.attrs['class'] = (existing_class + ' bg-light text-muted').strip()
                        field.widget.attrs['style'] = field.widget.attrs.get('style', '') + 'background-color:#e9ecef !important;color:#6c757d; !important'


# -------------------------
# Inline Formsets
# -------------------------
Kd_formset = inlineformset_factory(
    Kundenauftrag,
    Produkt,
    form=ProduktForm,
    can_delete=False,
    extra=1,
    max_num=8,
    fields=[ 
        'bezeichnung', 'p_auftragsmenge',
        'p_fertigungsauftrag', 'p_endtermin', 'p_infofeld', 'statusprodukt',
        'p_endtermin_wunsch', 'p_kalkpreis', 'p_serviceanfrage'
    ],
)

Prod_formset = inlineformset_factory(
    Produkt,
    Komponente,
    form=KomponenteForm,
    can_delete=False,
    extra=1,
    max_num=8,
    fields=[
        'bezeichnung', 'k_auftragsmenge', 'k_fertigungsauftrag',
        'k_endtermin', 'k_infofeld', 'statuskomponente'
    ],
)
