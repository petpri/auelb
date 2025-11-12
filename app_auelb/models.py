from django.db import models
from datetime import date


# STATUS: Auswahlfelder - Kundenauftrag
class StatusKundenauftrag(models.Model):
    kd_auswahl = models.CharField(max_length=20)

    def __str__(self):
        return self.kd_auswahl
    
    class Meta:
        db_table='tbl_statuskundenauftrage'
        verbose_name = "Status Kundenauftrag"
        verbose_name_plural = "Status Kundenaufträge"


# Kunde:
class Kunde(models.Model):
    kundennummer = models.IntegerField(verbose_name="Kundennummer")
    kundenname=models.CharField(max_length=50, verbose_name="Kundenname")

    def __str__(self):
        return f"{self.kundenname} ({self.kundennummer})"
    
    class Meta:
        db_table='tbl_kunde'
        verbose_name = "Kunde"
        verbose_name_plural = "Kunden"


# KUNDENAUFTRAG
class Kundenauftrag(models.Model):
    
    kundenauftrag = models.IntegerField(verbose_name="Kundenauftrag")
    kundenname = models.ForeignKey(Kunde, on_delete=models.CASCADE,related_name="kdname")
    v_endtermin=models.DateField(default=date.today)
    statuskundenauftrag = models.ForeignKey(StatusKundenauftrag, on_delete=models.CASCADE,related_name="rel_statkd", null=True, blank=True,default="---")
    foto = models.ImageField(upload_to='kundenauftraege/', blank=True, null=True,verbose_name="Bild") 
    kun_infofeld = models.TextField("Infofeld", blank=True, null=True)    

    def __str__(self):
        return str(self.kundenauftrag)
      
    class Meta:
        db_table='tbl_kundenauftrage'  # db_table: Tabelle in Datenbank wird mit tbl_marke benannt - wegen Kleinschreibung in xampp
        verbose_name = "Kundenauftrag"
        verbose_name_plural = "Kundenaufträge"

# Material:
class Material(models.Model):
    materialnummer = models.IntegerField(verbose_name="Materialnummer")
    bezeichnung=models.CharField(max_length=39, verbose_name="Bezeichnung")
    

    def __str__(self):
        return f"{self.bezeichnung} ({self.materialnummer})"
        
    
    class Meta:
        db_table='tbl_material'
        verbose_name = "Material"
        verbose_name_plural = "Materialien"

#Merkmale
class Merkmale(models.Model):
    materialnummer = models.OneToOneField(Material, on_delete=models.CASCADE,related_name="merkmale",null=True,blank=True)
    m_durchmesser=models.DecimalField(max_digits=6,decimal_places=3,null=True,blank=True)
    m_gewicht=models.DecimalField(max_digits=6,decimal_places=3,null=True,blank=True)
    m_bild = models.ImageField(upload_to="merkmale_bilder/", blank=True, null=True,verbose_name="Bild")
   

    def __str__(self):
        return str(self.materialnummer) 
    class Meta:
        db_table='tbl_merkmale'
        verbose_name = "Merkmal"
        verbose_name_plural = "Merkmale"

#Urblatt
class Urblatt(models.Model):
    materialnummer = models.OneToOneField(Material, on_delete=models.CASCADE,related_name="urblatt",null=True,blank=True)
    u_schnittwerkzeug=models.CharField(max_length=20, verbose_name="Schnittwerkzeug")
    u_bild = models.ImageField(upload_to="urblatt_bilder/", blank=True, null=True,verbose_name="Bild")

   
    def __str__(self):
        return str(self.materialnummer) 
    class Meta:
        db_table='tbl_urblatt'
        verbose_name = "Urblatt"
        verbose_name_plural = "Urblatt"


# Auswahlfelder - Produkt
class StatusProdukt(models.Model):
    produkt_auswahl = models.CharField(max_length=20)

    def __str__(self):
        return self.produkt_auswahl
    
    class Meta:
        db_table='tbl_statusprodukt'
        verbose_name = "Status Produkt"
        verbose_name_plural = "Status Produkte"




# PRODUKT
class Produkt(models.Model):

    kundenauftrag=models.ForeignKey(Kundenauftrag,on_delete=models.CASCADE,related_name="order_back_1")
    bezeichnung = models.ForeignKey(Material, on_delete=models.CASCADE,related_name="kdbezeichnung",null=True,blank=True)
    p_auftragsmenge=models.CharField(max_length=20,null=True,blank=True)
    p_fertigungsauftrag=models.CharField(max_length=10,null=True,blank=True)
    p_endtermin=models.DateField(default=date.today)
    p_endtermin_wunsch=models.DateField(default=date.today)
    p_serviceanfrage=models.CharField(max_length=20,null=True,blank=True)
    p_kalkpreis=models.CharField(max_length=20,null=True,blank=True)
    p_infofeld = models.TextField("Infofeld", blank=True, null=True)
    statusprodukt = models.ForeignKey(StatusProdukt, on_delete=models.CASCADE)


    def __str__(self):
        return str(self.bezeichnung) 

   
       
    class Meta:
        db_table='tbl_produkt'
        verbose_name = "Produkt"
        verbose_name_plural = "Produkte"


# Auswahlfelder - Komponente
class StatusKomponente(models.Model):
    komponente_auswahl = models.CharField(max_length=20)

    def __str__(self):
        return self.komponente_auswahl
    
    class Meta:
        db_table='tbl_statuskomponente'
        verbose_name = "Status Komponente"
        verbose_name_plural = "Status Komponenten "

# KOMPONENTE
class Komponente(models.Model):

    product=models.ForeignKey(Produkt,on_delete=models.CASCADE,related_name="order_back_2")
    bezeichnung = models.ForeignKey(Material, on_delete=models.CASCADE,related_name="kdbezeichnung_komp",null=True,blank=True)
    k_auftragsmenge=models.CharField(max_length=20,null=True,blank=True)
    k_fertigungsauftrag=models.CharField(max_length=10,null=True,blank=True)
    k_endtermin=models.DateField(default=date.today)
    k_serviceanfrage=models.CharField(max_length=20,null=True,blank=True)
    k_infofeld = models.TextField("Infofeld", blank=True, null=True)
    statuskomponente = models.ForeignKey(StatusKomponente, on_delete=models.CASCADE)
   
    def __str__(self):
        return str(self.bezeichnung) 
    class Meta:
        db_table='tbl_komponente'
        verbose_name = "Komponente"
        verbose_name_plural = "Komponenten"

# Create your models here.
