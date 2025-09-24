from django.contrib import admin

# Register your models here.

from .models import Produkt, Komponente, Kundenauftrag,StatusKomponente,StatusProdukt,StatusKundenauftrag,Kunde,Material,Merkmale,Urblatt

@admin.register(Kunde)
class KundenauftragAdmin(admin.ModelAdmin):
    list_display=['id','kundennummer','kundenname']

@admin.register(Material)
class MaterialAdmin(admin.ModelAdmin):
    list_display=['id','materialnummer','bezeichnung']

@admin.register(Kundenauftrag)
class KundenauftragAdmin(admin.ModelAdmin):
    list_display=['id','kundenauftrag','kundenname', 'statuskundenauftrag','v_endtermin']

@admin.register(Komponente)
class ProduktAdmin(admin.ModelAdmin):
    list_display=['id', 'bezeichnung', 'k_auftragsmenge', 'k_fertigungsauftrag', 'k_endtermin']

@admin.register(Produkt)
class ProduktAdmin(admin.ModelAdmin):
    list_display=['id', 'bezeichnung', 'p_auftragsmenge', 'p_fertigungsauftrag', 'p_endtermin']

@admin.register(Merkmale)
class MerkmaleAdmin(admin.ModelAdmin):
    list_display=['id','materialnummer', 'm_durchmesser', 'm_gewicht']

@admin.register(Urblatt)
class UrblattAdmin(admin.ModelAdmin):
    list_display=['id','materialnummer', 'u_schnittwerkzeug',"u_bild"]

@admin.register(StatusKomponente)
class StatusKomponenteAdmin(admin.ModelAdmin):
    list_display=['id','komponente_auswahl']

@admin.register(StatusProdukt)
class StatusProduktAdmin(admin.ModelAdmin):
    list_display=['id','produkt_auswahl']

@admin.register(StatusKundenauftrag)
class StatusKundenauftragtAdmin(admin.ModelAdmin):
    list_display=['id','kd_auswahl']



# Register your models here.
