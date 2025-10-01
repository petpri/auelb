from django.views.generic import UpdateView, DeleteView
from .models import Kundenauftrag, Produkt, Komponente, StatusKundenauftrag, StatusProdukt, Kunde, Material, Merkmale, Urblatt, StatusKomponente
from django.http import HttpResponse
from django.template import loader
from django.urls import reverse_lazy, reverse
from django.shortcuts import render, redirect, get_object_or_404
from .forms import KundenauftragForm, Kd_formset, Prod_formset, MerkmaleForm, UrblattForm
from django.db.models import Q

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

    theirdata = theirdata.order_by('v_endtermin')

    if my_select and my_select.strip() != "" and my_select != "1":
        theirdata = theirdata.filter(statuskundenauftrag__id=my_select)
    if searchsuche:
        theirdata = theirdata.filter(kundenauftrag__icontains=searchsuche)
    if kundennummer:
        theirdata = theirdata.filter(kundenname__kundennummer__icontains=kundennummer)
    if materialsuche:
        theirdata = theirdata.filter(
            Q(order_back_1__bezeichnung__materialnummer__icontains=materialsuche) |
            Q(order_back_1__order_back_2__bezeichnung__materialnummer__icontains=materialsuche)
        )
    if fertigungsauftrag:
        theirdata = theirdata.filter(
            Q(order_back_1__p_fertigungsauftrag__icontains=fertigungsauftrag) |
            Q(order_back_1__order_back_2__k_fertigungsauftrag__icontains=fertigungsauftrag)
        )
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
    'mode_label': "Produktiv",
    'from_param': 'produktiv',  # wichtig für Button
    'current_view': 'produktiv',  # wichtig für P/K Buttons
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

    theirdata = theirdata.order_by('-v_endtermin')

    if my_select and my_select.strip() != "" and my_select != "1":
        theirdata = theirdata.filter(statuskundenauftrag__id=my_select)
    if searchsuche:
        theirdata = theirdata.filter(kundenauftrag__icontains=searchsuche)
    if kundennummer:
        theirdata = theirdata.filter(kundenname__kundennummer__icontains=kundennummer)
    if materialsuche:
        theirdata = theirdata.filter(
            Q(order_back_1__bezeichnung__materialnummer__icontains=materialsuche) |
            Q(order_back_1__order_back_2__bezeichnung__materialnummer__icontains=materialsuche)
        )
    if fertigungsauftrag:
        theirdata = theirdata.filter(
            Q(order_back_1__p_fertigungsauftrag__icontains=fertigungsauftrag) |
            Q(order_back_1__order_back_2__k_fertigungsauftrag__icontains=fertigungsauftrag)
        )
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
    'mode_label': "Archiv",
    'from_param': 'archiv',
    'current_view': 'archiv',  # wichtig für P/K Buttons
})


# -----------------------------
# Kundenauftrag bearbeiten
# -----------------------------
class KundenauftragUpdate(UpdateView):
    model = Kundenauftrag
    form_class = KundenauftragForm
    template_name = 'app_auelb/kundenauftrag_bearbeiten.html'

    def form_valid(self, form):
        # Zuerst Objekt speichern, aber commit=False, damit wir das Foto setzen können
        self.object = form.save(commit=False)
        if 'foto' in self.request.FILES:
            self.object.foto = self.request.FILES['foto']
        self.object.save()

        # Status-Logik beibehalten
        if self.object.statuskundenauftrag and self.object.statuskundenauftrag.kd_auswahl == "Geliefert":
            gelieferter_status = StatusProdukt.objects.get(produkt_auswahl="Geliefert")
            for produkt in self.object.order_back_1.all():
                produkt.statusprodukt = gelieferter_status
                produkt.save()
                gelieferter_komp_status = StatusKomponente.objects.get(komponente_auswahl="Geliefert")
                for komp in produkt.order_back_2.all():
                    komp.statuskomponente = gelieferter_komp_status
                    komp.save()

        return super().form_valid(form)

    def get_success_url(self):
        base_url = reverse('kundenauftrag_bearbeiten', kwargs={'pk': self.object.pk})
        params = self.request.GET.urlencode()
        return f"{base_url}?{params}" if params else base_url



# -----------------------------
# Merkmale bearbeiten
# -----------------------------
def merkmale_bearbeiten(request, pk):
    material = get_object_or_404(Material, pk=pk)
    obj, created = Merkmale.objects.get_or_create(materialnummer=material)

    from_param = request.GET.get("from", "produktiv")
    back_url = reverse("auftragsliste_geliefert") if from_param.lower() in ["archiv", "geliefert"] else reverse("auftragsliste_nicht_geliefert")
    back_label = "ARCHIV" if from_param.lower() in ["archiv", "geliefert"] else "PRODUKTIV"

    query_params = request.GET.copy()
    if "from" in query_params:
        del query_params["from"]
    query_string = query_params.urlencode()

    if request.method == "POST":
        form = MerkmaleForm(request.POST, request.FILES, instance=obj)
        if form.is_valid():
            form.save()
            return redirect(f"{back_url}?{query_string}" if query_string else back_url)
    else:
        form = MerkmaleForm(instance=obj)

    return render(request, "app_auelb/merkmale_bearbeiten.html", {
        "object": obj,
        "form": form,
        "mode_label": "MERKMALE",
        "back_url": f"{back_url}?{query_string}" if query_string else back_url,
        "back_label": back_label,
        "show_save_button": True,
    })


# -----------------------------
# Urblatt bearbeiten
# -----------------------------
def urblatt_bearbeiten(request, pk):
    material = get_object_or_404(Material, pk=pk)
    obj, created = Urblatt.objects.get_or_create(materialnummer=material)

    from_param = request.GET.get("from", "produktiv")
    back_url = reverse("auftragsliste_geliefert") if from_param.lower() in ["archiv", "geliefert"] else reverse("auftragsliste_nicht_geliefert")
    back_label = "ARCHIV" if from_param.lower() in ["archiv", "geliefert"] else "PRODUKTIV"

    query_params = request.GET.copy()
    if "from" in query_params:
        del query_params["from"]
    query_string = query_params.urlencode()

    if request.method == "POST":
        form = UrblattForm(request.POST, request.FILES, instance=obj)
        if form.is_valid():
            form.save()
            return redirect(f"{back_url}?{query_string}" if query_string else back_url)
    else:
        form = UrblattForm(instance=obj)

    return render(request, "app_auelb/urblatt_bearbeiten.html", {
        "object": obj,
        "form": form,
        "mode_label": "URBLATT",
        "back_url": f"{back_url}?{query_string}" if query_string else back_url,
        "back_label": back_label,
        "show_save_button": True,
    })


# -----------------------------
# Kundenauftrag NEU
# -----------------------------
def create_kundenauftrag(request):
    if request.method == 'POST':
        form = KundenauftragForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('auftragsliste_nicht_geliefert')
    else:
        form = KundenauftragForm()
    return render(request, 'app_auelb/auftrag_neu.html', {'form': form})


# ------------------------------
# Kundenauftrag UPDATE (A und P)
# ------------------------------
def kundenauftragUpdate(request, pk):
    kundenauftrag = get_object_or_404(Kundenauftrag, pk=pk)
    formset = Kd_formset(request.POST or None, instance=kundenauftrag)

    from_param = request.GET.get("from", "produktiv").lower()

    if from_param == "archiv":
        back_url = reverse("auftragsliste_geliefert")
        back_label = "ARCHIV"
    else:
        back_url = reverse("auftragsliste_nicht_geliefert")
        back_label = "PRODUKTIV"

    query_params = request.GET.copy() or request.POST.copy()
    query_string = query_params.urlencode()

    if request.method == "POST" and formset.is_valid():
        formset.save()
        base_url = reverse('kundenauftrag_update', kwargs={'pk': kundenauftrag.pk})
        return redirect(f"{base_url}?{query_string}" if query_string else base_url)

    return render(request, 'app_auelb/auftrag_auffrischen.html', {
        'kundenauftrag': kundenauftrag,
        'formset': formset,
        'query_string': query_string,
        'from_param': from_param,
        'back_url': back_url,
        'back_label': back_label,
        'mode_label': "KUNDENAUFTRAG",
    })




# ------------------------------
# Produkt UPDATE (K)
# ------------------------------
def produktUpdate(request, pk):
    produkt = get_object_or_404(Produkt, pk=pk)
    formset = Prod_formset(request.POST or None, instance=produkt)

    from_param = request.GET.get("from", "produktiv").lower()

    if from_param == "archiv":
        back_url = reverse("auftragsliste_geliefert")
        back_label = "ARCHIV"
    else:
        back_url = reverse("auftragsliste_nicht_geliefert")
        back_label = "PRODUKTIV"

    query_params = request.GET.copy() or request.POST.copy()
    query_string = query_params.urlencode()

    if request.method == "POST" and formset.is_valid():
        formset.save()
        base_url = reverse('produkt_update', kwargs={'pk': produkt.pk})
        return redirect(f"{base_url}?{query_string}" if query_string else base_url)

    return render(request, 'app_auelb/auftrag_auffrischen_1.html', {
        'produkt': produkt,
        'formset': formset,
        'query_string': query_string,
        'from_param': from_param,
        'back_url': back_url,
        'back_label': back_label,
        'mode_label': "KOMPONENTE",
    })


# -----------------------------
# Kundenauftragsliste
# -----------------------------
def kd_auftragsliste_view(request):
    theirdata = Kundenauftrag.objects.all()
    if 'searchsuche' in request.GET:
        searchsuche = request.GET['searchsuche']
        if 'my_select' in request.GET:
            my_select = request.GET['my_select']
            theirdata = Kundenauftrag.objects.filter(statuskundenauftrag=my_select).filter(kundenauftrag__icontains=searchsuche)
            if my_select == "1":
                theirdata = Kundenauftrag.objects.filter(kundenauftrag__icontains=searchsuche)

    mydata = Komponente.objects.all()
    yourdata = Produkt.objects.all()
    data = StatusKundenauftrag.objects.all()
    template = loader.get_template('app_auelb/auftrag_kd_auftragsliste.html')

    context = {
        'meine_daten': mydata,
        'deine_daten': yourdata,
        'ihre_daten': theirdata,
        'data': data,
    }

    result = template.render(context, request)
    return HttpResponse(result)
