from django.db import models
from datetime import date


# STATUS: Auswahlfelder - Kundenauftrag
class StatusKundenauftrag(models.Model):
    kd_auswahl = models.CharField(max_length=20, default="---")

    def __str__(self):
        return self.kd_auswahl
    
    class Meta:
        db_table='tbl_statuskundenauftrage'

# Kunde:
class Kunde(models.Model):
    kundennummer = models.IntegerField(verbose_name="Kundennummer")
    kundenname=models.CharField(max_length=50, verbose_name="Kundenname")

    def __str__(self):
        return f"{self.kundenname} ({self.kundennummer})"
    
    class Meta:
        db_table='tbl_kunde'


# KUNDENAUFTRAG
class Kundenauftrag(models.Model):
    
    kundenauftrag = models.IntegerField(verbose_name="Kundenauftrag")
    kundenname = models.ForeignKey(Kunde, on_delete=models.CASCADE,related_name="kdname")
    statuskundenauftrag = models.ForeignKey(StatusKundenauftrag, on_delete=models.CASCADE, default='---',related_name="rel_statkd", null=True, blank=True)
         

    def __str__(self):
        return str(self.kundenauftrag)
      
    class Meta:
        db_table='tbl_kundenauftrage'  # db_table: Tabelle in Datenbank wird mit tbl_marke benannt - wegen Kleinschreibung in xampp

# Material:
class Material(models.Model):
    materialnummer = models.IntegerField(verbose_name="Materialnummer")
    bezeichnung=models.CharField(max_length=39, verbose_name="Bezeichnung")

    def __str__(self):
        return f"{self.bezeichnung} ({self.materialnummer})"
        
    
    class Meta:
        db_table='tbl_material'


# Auswahlfelder - Produkt
class StatusProdukt(models.Model):
    produkt_auswahl = models.CharField(max_length=20)

    def __str__(self):
        return self.produkt_auswahl
    
    class Meta:
        db_table='tbl_statusprodukt'

# PRODUKT
class Produkt(models.Model):

    kundenauftrag=models.ForeignKey(Kundenauftrag,on_delete=models.CASCADE,related_name="order_back_1")
    bezeichnung = models.ForeignKey(Material, on_delete=models.CASCADE,related_name="kdbezeichnung",null=True,blank=True)
    p_auftragsmenge=models.CharField(max_length=20,null=True,blank=True)
    p_fertigungsauftrag=models.CharField(max_length=10,null=True,blank=True)
    p_endtermin=models.DateField(default=date.today)
    statusprodukt = models.ForeignKey(StatusProdukt, on_delete=models.CASCADE,default='---')


    def __str__(self):
        return str(self.bezeichnung) 

   
       
    class Meta:
        db_table='tbl_produkt'


# Auswahlfelder - Komponente
class StatusKomponente(models.Model):
    komponente_auswahl = models.CharField(max_length=20)

    def __str__(self):
        return self.komponente_auswahl
    
    class Meta:
        db_table='tbl_statuskomponente'

# KOMPONENTE
class Komponente(models.Model):

    product=models.ForeignKey(Produkt,on_delete=models.CASCADE,related_name="order_back_2")
    bezeichnung = models.ForeignKey(Material, on_delete=models.CASCADE,related_name="kdbezeichnung_komp",null=True,blank=True)
    k_auftragsmenge=models.CharField(max_length=20,null=True,blank=True)
    k_fertigungsauftrag=models.CharField(max_length=10,null=True,blank=True)
    k_endtermin=models.DateField(default=date.today)
    statuskomponente = models.ForeignKey(StatusKomponente, on_delete=models.CASCADE,default='---')
   
    def __str__(self):
        return str(self.bezeichnung) 
    class Meta:
        db_table='tbl_komponente'

# Create your models here.
