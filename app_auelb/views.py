from django.views.generic import UpdateView, DeleteView
from .models import Kundenauftrag, Produkt, Komponente, StatusKundenauftrag,StatusProdukt,Kunde,Material,Merkmale,Urblatt,StatusKomponente
from django.http import HttpResponse
from django.template import loader
from django.urls import reverse_lazy
from django.shortcuts import render, redirect, get_object_or_404
from .forms import KundenauftragForm, Kd_formset, Prod_formset,MerkmaleForm,UrblattForm
from django.db.models import Q



#AUFTRAGSLISTE select und input Filter


# ------------------------------
# Nicht gelieferte Aufträge
# ------------------------------
def auftragsliste_nicht_geliefert_view(request):
    theirdata = Kundenauftrag.objects.exclude(statuskundenauftrag__kd_auswahl__iexact="Geliefert")

    searchsuche = request.GET.get('searchsuche')
    materialsuche = request.GET.get('materialsuche')
    my_select = request.GET.get('my_select')
    kundennummer = request.GET.get('kundennummer')
    fertigungsauftrag = request.GET.get('fertigungsauftrag')
    status = request.GET.get('status')

    # Status Kundenauftrag
    if my_select and my_select.strip() != "" and my_select != "1":
        theirdata = theirdata.filter(statuskundenauftrag__kd_auswahl__iexact=my_select)

    # Kundenauftrag
    if searchsuche:
        theirdata = theirdata.filter(kundenauftrag__icontains=searchsuche)

    # Kundennummer
    if kundennummer:
        theirdata = theirdata.filter(kundenname__kundennummer__icontains=kundennummer)

    # Materialnummer
    if materialsuche:
        theirdata = theirdata.filter(
            Q(order_back_1__bezeichnung__materialnummer__icontains=materialsuche) |
            Q(order_back_1__order_back_2__bezeichnung__materialnummer__icontains=materialsuche)
        )

    # Fertigungsauftrag
    if fertigungsauftrag:
        theirdata = theirdata.filter(
            Q(order_back_1__p_fertigungsauftrag__icontains=fertigungsauftrag) |
            Q(order_back_1__order_back_2__k_fertigungsauftrag__icontains=fertigungsauftrag)
        )

    # Status Produkt/Komponente
    if status:
        theirdata = theirdata.filter(
            Q(order_back_1__statusprodukt__produkt_auswahl__icontains=status) |
            Q(order_back_1__order_back_2__statuskomponente__komponente_auswahl__icontains=status)
        )

    theirdata = theirdata.distinct()

    return render(request, 'app_auelb/auftrag_auftragsliste.html', {
        'ihre_daten': theirdata,
        'meine_daten': Komponente.objects.all(),
        'deine_daten': Produkt.objects.all(),
        'data': StatusKundenauftrag.objects.all(),
        'mode_label': "Produktiv",  # <- hier hinzugefügt
    })


# ------------------------------
# Gelieferte Aufträge
# ------------------------------
def auftragsliste_geliefert_view(request):
    theirdata = Kundenauftrag.objects.filter(statuskundenauftrag__kd_auswahl__iexact="Geliefert")

    searchsuche = request.GET.get('searchsuche')
    materialsuche = request.GET.get('materialsuche')
    my_select = request.GET.get('my_select')
    kundennummer = request.GET.get('kundennummer')
    fertigungsauftrag = request.GET.get('fertigungsauftrag')
    status = request.GET.get('status')

    # Status Kundenauftrag
    if my_select and my_select.strip() != "" and my_select != "1":
        theirdata = theirdata.filter(statuskundenauftrag__kd_auswahl__iexact=my_select)

    # Kundenauftrag
    if searchsuche:
        theirdata = theirdata.filter(kundenauftrag__icontains=searchsuche)

    # Kundennummer
    if kundennummer:
        theirdata = theirdata.filter(kundenname__kundennummer__icontains=kundennummer)

    # Materialnummer
    if materialsuche:
        theirdata = theirdata.filter(
            Q(order_back_1__bezeichnung__materialnummer__icontains=materialsuche) |
            Q(order_back_1__order_back_2__bezeichnung__materialnummer__icontains=materialsuche)
        )

    # Fertigungsauftrag
    if fertigungsauftrag:
        theirdata = theirdata.filter(
            Q(order_back_1__p_fertigungsauftrag__icontains=fertigungsauftrag) |
            Q(order_back_1__order_back_2__k_fertigungsauftrag__icontains=fertigungsauftrag)
        )

    # Status Produkt/Komponente
    if status:
        theirdata = theirdata.filter(
            Q(order_back_1__statusprodukt__produkt_auswahl__icontains=status) |
            Q(order_back_1__order_back_2__statuskomponente__komponente_auswahl__icontains=status)
        )

    theirdata = theirdata.distinct()

    return render(request, 'app_auelb/auftrag_auftragsliste_geliefert.html', {
        'ihre_daten': theirdata,
        'meine_daten': Komponente.objects.all(),
        'deine_daten': Produkt.objects.all(),
        'data': StatusKundenauftrag.objects.all(),
        'mode_label': "Archiv",  # <- hier hinzugefügt
    })



# Kundenauftrag bearbeiten
class KundenauftragUpdate(UpdateView):
    model = Kundenauftrag
    form_class = KundenauftragForm
    template_name = 'app_auelb/kundenauftrag_bearbeiten.html'

    def form_valid(self, form):
        # Speichern, aber noch nicht endgültig in DB
        response = super().form_valid(form)
        
        # Prüfen, ob der Kundenauftrag auf "Geliefert" gesetzt wurde
        if self.object.statuskundenauftrag and self.object.statuskundenauftrag.kd_auswahl == "Geliefert":
            # Alle zugehörigen Produkte auf Geliefert setzen
            gelieferter_status = StatusProdukt.objects.get(produkt_auswahl="Geliefert")
            for produkt in self.object.order_back_1.all():
                produkt.statusprodukt = gelieferter_status
                produkt.save()

                # Alle Komponenten dieses Produkts auf Geliefert setzen
                gelieferter_komp_status = StatusKomponente.objects.get(komponente_auswahl="Geliefert")
                for komp in produkt.order_back_2.all():
                    komp.statuskomponente = gelieferter_komp_status
                    komp.save()
        
        return response

    def get_success_url(self):
        return reverse_lazy('kundenauftrag_update', kwargs={'pk': self.object.pk})

# Merkmale bearbeiten
class MerkmaleUpdate(UpdateView):
    model = Merkmale
    form_class = MerkmaleForm
    template_name = 'app_auelb/merkmale_bearbeiten.html'

    def get_object(self, queryset=None):
        pk = self.kwargs.get('pk')
        # Nur existierendes Objekt holen, kein get_or_create
        return get_object_or_404(Merkmale, pk=pk)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        origin = self.request.GET.get("from", "nicht-geliefert")
        if origin == "geliefert":
            context["back_url"] = reverse_lazy('auftragsliste_geliefert')
            context["back_label"] = "ARCHIV"
            context["mode_label"] = "Archiv"
        else:
            context["back_url"] = reverse_lazy('auftragsliste_nicht_geliefert')
            context["back_label"] = "PRODUKTIV"
            context["mode_label"] = "Produktiv"

        # Navbar + Bild-Buttons anzeigen nur im Produktivmodus
        context["show_save_button"] = context["mode_label"] != "Archiv"
        return context

    def form_valid(self, form):
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('merkmale_bearbeiten', kwargs={'pk': self.get_object().pk})



# Urblatt bearbeiten
class UrblattUpdate(UpdateView):
    model = Urblatt
    form_class = UrblattForm
    template_name = 'app_auelb/urblatt_bearbeiten.html'

    def get_object(self, queryset=None):
        pk = self.kwargs.get('pk')
        return get_object_or_404(Urblatt, pk=pk)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        origin = self.request.GET.get("from", "nicht-geliefert")
        if origin == "geliefert":
            context["back_url"] = reverse_lazy('auftragsliste_geliefert')
            context["back_label"] = "ARCHIV"
            context["mode_label"] = "Archiv"
        else:
            context["back_url"] = reverse_lazy('auftragsliste_nicht_geliefert')
            context["back_label"] = "PRODUKTIV"
            context["mode_label"] = "Produktiv"

        context["show_save_button"] = context["mode_label"] != "Archiv"
        return context

    def form_valid(self, form):
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('urblatt_bearbeiten', kwargs={'pk': self.get_object().pk})




#Kundenauftrag NEU
def create_kundenauftrag(request):
    if request.method == 'POST':
        form = KundenauftragForm(request.POST)
        if form.is_valid():
            form.save()  # Saves the form data to the database
            return redirect('auftragsliste_nicht_geliefert')  # Redirect to a list of posts
    else:
        form = KundenauftragForm()
    return render(request, 'app_auelb/auftrag_neu.html', {'form': form})

# Kundenauftrag UPDATE
def kundenauftragUpdate(request, pk):
    kundenauftrag = get_object_or_404(Kundenauftrag, pk=pk)
    formset = Kd_formset(request.POST or None, instance=kundenauftrag)
    if request.method == "POST":
        if formset.is_valid():
            formset.save()
            return redirect('kundenauftrag_update',pk=kundenauftrag.pk)
            #return redirect('auftrag_auftragsliste')
        else:
            print("Formular ist ungültig!")
            print(formset.errors)
            
    return render(request, 'app_auelb/auftrag_auffrischen.html',
        context= {
            'kundenauftrag': kundenauftrag,
            'formset' : formset,
            }
        )

# Produkt UPDATE
def produktUpdate(request, pk):
    produkt = get_object_or_404(Produkt, pk=pk)
    formset = Prod_formset(request.POST or None, instance=produkt)
    if request.method == "POST":
        if formset.is_valid():
            formset.save()
            return redirect('produkt_update',pk=produkt.pk)
            #return redirect('auftrag_auftragsliste')
    return render(request, 'app_auelb/auftrag_auffrischen_1.html',
        context= {
            'produkt': produkt,
            'formset' : formset,   
            }
        )

def kd_auftragsliste_view(request):

    if 'searchsuche' in request.GET:
        searchsuche = request.GET['searchsuche']
        if 'my_select' in request.GET:
            my_select = request.GET['my_select']
            theirdata = Kundenauftrag.objects.filter(statuskundenauftrag = my_select).filter(kundenauftrag__icontains = searchsuche)
            if my_select == "1":  #5 ist die id vom Status Modell
                theirdata = Kundenauftrag.objects.filter(kundenauftrag__icontains = searchsuche)
                
    else:
        theirdata = Kundenauftrag.objects.all()


    mydata = Komponente.objects.all()
    yourdata = Produkt.objects.all()
    data=StatusKundenauftrag.objects.all()
    template = loader.get_template('app_auelb/auftrag_kd_auftragsliste.html') 

    context = {
        'meine_daten': mydata,
        'deine_daten': yourdata,
        'ihre_daten': theirdata,
        'data' : data,            
    }
   
    result = template.render(context, request)
    return HttpResponse(result)

# Create your views here.




