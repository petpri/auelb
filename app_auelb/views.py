from django.views.generic import UpdateView, DeleteView
from .models import Kundenauftrag, Produkt, Komponente, StatusKundenauftrag,StatusProdukt,Kunde,Material
from django.http import HttpResponse
from django.template import loader
from django.urls import reverse_lazy
from django.shortcuts import render, redirect, get_object_or_404
from .forms import KundenauftragForm, Kd_formset, Prod_formset



#AUFTRAGSLISTE select und input Filter
def auftragsliste_view(request):

    if 'searchsuche' in request.GET:
        searchsuche = request.GET['searchsuche']
        if 'my_select' in request.GET:
            my_select = request.GET['my_select']
            theirdata = Kundenauftrag.objects.filter(statuskundenauftrag = my_select).filter(kundenauftrag__icontains = searchsuche)
            if my_select == "1":  
                theirdata = Kundenauftrag.objects.filter(kundenauftrag__icontains = searchsuche)
                
    else:
        theirdata = Kundenauftrag.objects.all()

    mydata = Komponente.objects.all()
    yourdata = Produkt.objects.all()
    data=StatusKundenauftrag.objects.all()
    template = loader.get_template('app_auelb/auftrag_auftragsliste.html') 

    context = {
        'meine_daten': mydata,
        'deine_daten': yourdata,
        'ihre_daten': theirdata,
        'data' : data,      
    }
   
    result = template.render(context, request)
    return HttpResponse(result)

# Kundenauftrag bearbeiten
class KundenauftragUpdate(UpdateView):
    model=Kundenauftrag
    form_class = KundenauftragForm
    template_name='app_auelb/kundenauftrag_bearbeiten.html'
    #fields=('id', 'kundenauftrag','kundenname','statuskundenauftrag') # 25.06.2025 dazu
    #success_url=reverse_lazy('auftrag_auftragsliste')

    def get_success_url(self):
        return reverse_lazy('kundenauftrag_bearbeiten', kwargs={'pk': self.get_object().pk})


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




