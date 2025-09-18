from django.views.generic import UpdateView, DeleteView
from .models import Kundenauftrag, Produkt, Komponente, StatusKundenauftrag,StatusProdukt,Kunde,Material,Merkmale,Urblatt
from django.http import HttpResponse
from django.template import loader
from django.urls import reverse_lazy
from django.shortcuts import render, redirect, get_object_or_404
from .forms import KundenauftragForm, Kd_formset, Prod_formset,MerkmaleForm,UrblattForm
from django.db.models import Q



#AUFTRAGSLISTE select und input Filter
from django.db.models import Q
from django.http import HttpResponse
from django.template import loader
from .models import Kundenauftrag, Komponente, Produkt, StatusKundenauftrag

from django.db.models import Q
from django.http import HttpResponse
from django.template import loader
from .models import Kundenauftrag, Komponente, Produkt, StatusKundenauftrag

def auftragsliste_view(request):
    theirdata = Kundenauftrag.objects.all()

    # GET-Parameter
    searchsuche = request.GET.get('searchsuche')
    materialsuche = request.GET.get('materialsuche')
    my_select = request.GET.get('my_select')
    kundennummer = request.GET.get('kundennummer')
    fertigungsauftrag = request.GET.get('fertigungsauftrag')
    status = request.GET.get('status')
    show_delivered = request.GET.get('show_delivered')  # Toggle

    if show_delivered == "1":
        # Nur Geliefert anzeigen
        theirdata = theirdata.filter(statuskundenauftrag__kd_auswahl__iexact="Geliefert")
    else:
        # Standard: Geliefert ausblenden
        theirdata = theirdata.exclude(statuskundenauftrag__kd_auswahl__iexact="Geliefert")

    # Kundenauftrag filtern
    if searchsuche:
        theirdata = theirdata.filter(kundenauftrag__icontains=searchsuche)

    # Kundennummer filtern
    if kundennummer:
        theirdata = theirdata.filter(kundenname__kundennummer__icontains=kundennummer)

    # Status Kundenauftrag filtern (außer „Geliefert“, da über show_delivered gesteuert)
    if my_select and my_select.strip() != "":
        if my_select != "1":
            theirdata = theirdata.filter(statuskundenauftrag=my_select)

    # Materialnummer filtern
    if materialsuche:
        theirdata = theirdata.filter(
            Q(order_back_1__bezeichnung__materialnummer__icontains=materialsuche) |
            Q(order_back_1__order_back_2__bezeichnung__materialnummer__icontains=materialsuche)
        )

    # Fertigungsauftrag filtern
    if fertigungsauftrag:
        theirdata = theirdata.filter(
            Q(order_back_1__p_fertigungsauftrag__icontains=fertigungsauftrag) |
            Q(order_back_1__order_back_2__k_fertigungsauftrag__icontains=fertigungsauftrag)
        )

    # Status Produkt/Komponente filtern
    if status:
        theirdata = theirdata.filter(
            Q(order_back_1__statusprodukt__icontains=status) |
            Q(order_back_1__order_back_2__statuskomponente__icontains=status)
        )

    # Andere Daten
    mydata = Komponente.objects.all()
    yourdata = Produkt.objects.all()
    data = StatusKundenauftrag.objects.all()

    template = loader.get_template('app_auelb/auftrag_auftragsliste.html')
    context = {
        'meine_daten': mydata,
        'deine_daten': yourdata,
        'ihre_daten': theirdata.distinct(),
        'data': data,
        'show_delivered': show_delivered,
    }

    return HttpResponse(template.render(context, request))


# Kundenauftrag bearbeiten
class KundenauftragUpdate(UpdateView):
    model=Kundenauftrag
    form_class = KundenauftragForm
    template_name='app_auelb/kundenauftrag_bearbeiten.html'
    #fields=('id', 'kundenauftrag','kundenname','statuskundenauftrag') # 25.06.2025 dazu
    #success_url=reverse_lazy('auftrag_auftragsliste')

    def get_success_url(self):
        return reverse_lazy('kundenauftrag_bearbeiten', kwargs={'pk': self.get_object().pk})

# Merkmale bearbeiten
class MerkmaleUpdate(UpdateView):
    model = Merkmale
    form_class = MerkmaleForm
    template_name = 'app_auelb/merkmale_bearbeiten.html'

    def get_object(self, queryset=None):
        pk = self.kwargs.get('pk')
        # Versuch, das Objekt zu holen
        obj = Merkmale.objects.filter(pk=pk).first()
        if not obj:
            # Objekt existiert nicht → erstelle ein neues
            obj = Merkmale(pk=pk)
            obj.save()
        return obj

    def get_success_url(self):
        return reverse_lazy('merkmale_bearbeiten', kwargs={'pk': self.get_object().pk})

# Urblatt bearbeiten
class UrblattUpdate(UpdateView):
    model = Urblatt
    form_class = UrblattForm
    template_name = 'app_auelb/urblatt_bearbeiten.html'

    def get_object(self, queryset=None):
        pk = self.kwargs.get('pk')
        # Versuch, das Objekt zu holen
        obj = Urblatt.objects.filter(pk=pk).first()
        if not obj:
            # Objekt existiert nicht → erstelle ein neues
            obj = Urblatt(pk=pk)
            obj.save()
        return obj

    def get_success_url(self):
        return reverse_lazy('urblatt_bearbeiten', kwargs={'pk': self.get_object().pk})

#Kundenauftrag NEU
def create_kundenauftrag(request):
    if request.method == 'POST':
        form = KundenauftragForm(request.POST)
        if form.is_valid():
            form.save()  # Saves the form data to the database
            return redirect('auftrag_auftragsliste')  # Redirect to a list of posts
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
            return redirect('auftrag_auffrischen',pk=kundenauftrag.pk)
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
            return redirect('auftrag_auffrischen_1',pk=produkt.pk)
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




