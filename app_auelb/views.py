from django.contrib.auth.decorators import login_required
from django.views.generic import UpdateView
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.db.models import Q
from .models import (
    Kundenauftrag, Produkt, Komponente, StatusKundenauftrag,
    StatusProdukt, Kunde, Material, Merkmale, Urblatt, StatusKomponente
)
from .forms import KundenauftragForm, Kd_formset, Prod_formset, MerkmaleForm, UrblattForm, KomponenteForm
from django.contrib.auth.models import User, Group
from django_select2.forms import Select2Widget


class MaterialWidget(Select2Widget):
    def __init__(self, attrs=None):
        default_attrs = {"data-placeholder": "Material suchen", "style": "width: 450px;"}
        if attrs:
            default_attrs.update(attrs)
        super().__init__(attrs=default_attrs)

# ------------------------
# Startseite
# ------------------------
@login_required
def home(request):
    """
    Startseite – leitet je nach Benutzer auf passende Auftragsliste.
    """
    user_groups = [g.name for g in request.user.groups.all()]

    if "TVK" in user_groups or "PPS_MAWI" in user_groups:
        return redirect("auftragsliste_nicht_geliefert")
    else:
        return redirect("kd_auftragsliste")


# ------------------------------
# Hilfsfunktion für Benutzerrechte
# ------------------------------
# Hinweis: Diese Funktion user_can_edit() wird in der kundenauftragUpdate View nicht mehr benötigt, 
# da die Logik in die Formulare verschoben wurde. Sie wird nur noch für die Listenansichten verwendet.
def user_can_edit(user):
    group = user.groups.first()
    if not group:
        return False, []
    group_name = group.name
    readonly_fields = []
    if group_name == "TVK":
        can_edit = True
        readonly_fields = ["p_kalkpreis", "p_serviceanfrage", "p_endtermin", "p_fertigungsauftrag"]
    elif group_name == "PPS_MAWI":
        can_edit = True
    elif group_name == "Produktion":  # Produktion hat nur read-only Rechte
        can_edit = False
        readonly_fields = ["bezeichnung", "k_auftragsmenge", "k_fertigungsauftrag", "k_endtermin", "statuskomponente", "k_infofeld",]
    else:  # Meister
        can_edit = False
    return can_edit, readonly_fields


# ------------------------------
# Auftragslisten
# ------------------------------
@login_required
def auftragsliste_nicht_geliefert_view(request):
    # ... (Logik für die Listenansicht bleibt unverändert) ...
    theirdata = Kundenauftrag.objects.exclude(statuskundenauftrag__kd_auswahl__iexact="Geliefert")
    # ... (Filterlogik unverändert, verwendet die alten related_names order_back_1/order_back_2) ...
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
            Q(order_back_1__bezeichnung__materialnummer__icontains=materialsuche)
            | Q(order_back_1__order_back_2__bezeichnung__materialnummer__icontains=materialsuche)
        )
    if fertigungsauftrag:
        theirdata = theirdata.filter(
            Q(order_back_1__p_fertigungsauftrag__icontains=fertigungsauftrag)
            | Q(order_back_1__order_back_2__k_fertigungsauftrag__icontains=fertigungsauftrag)
        )
    if status:
        theirdata = theirdata.filter(
            Q(order_back_1__statusprodukt__produkt_auswahl__icontains=status)
            | Q(order_back_1__order_back_2__statuskomponente__komponente_auswahl__icontains=status)
        )

    theirdata = theirdata.distinct()
    can_edit, readonly_fields = user_can_edit(request.user)

    return render(request, 'app_auelb/auftrag_auftragsliste.html', {
        'ihre_daten': theirdata,
        'meine_daten': Komponente.objects.all(),
        'deine_daten': Produkt.objects.all(),
        'data': StatusKundenauftrag.objects.all(),
        'mode_label': "Produktiv",
        'from_param': 'produktiv',
        'current_view': 'produktiv',
        'can_edit': can_edit,
        'readonly_fields': readonly_fields,
    })


@login_required
def auftragsliste_geliefert_view(request):
    # ... (Logik für die Listenansicht bleibt unverändert) ...
    theirdata = Kundenauftrag.objects.filter(statuskundenauftrag__kd_auswahl__iexact="Geliefert")
    # ... (Filterlogik unverändert, verwendet die alten related_names order_back_1/order_back_2) ...
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
            Q(order_back_1__bezeichnung__materialnummer__icontains=materialsuche)
            | Q(order_back_1__order_back_2__bezeichnung__materialnummer__icontains=materialsuche)
        )
    if fertigungsauftrag:
        theirdata = theirdata.filter(
            Q(order_back_1__p_fertigungsauftrag__icontains=fertigungsauftrag)
            | Q(order_back_1__order_back_2__k_fertigungsauftrag__icontains=fertigungsauftrag)
        )
    if status:
        theirdata = theirdata.filter(
            Q(order_back_1__statusprodukt__produkt_auswahl__icontains=status)
            | Q(order_back_1__order_back_2__statuskomponente__komponente_auswahl__icontains=status)
        )

    theirdata = theirdata.distinct()
    can_edit, readonly_fields = user_can_edit(request.user)

    return render(request, 'app_auelb/auftrag_auftragsliste_geliefert.html', {
        'ihre_daten': theirdata,
        'meine_daten': Komponente.objects.all(),
        'deine_daten': Produkt.objects.all(),
        'data': StatusKundenauftrag.objects.all(),
        'mode_label': "Archiv",
        'from_param': 'archiv',
        'current_view': 'archiv',
        'can_edit': can_edit,
        'readonly_fields': readonly_fields,
    })


# ------------------------------
# Kundenauftrag bearbeiten (Class-based)
# ------------------------------
class KundenauftragUpdate(UpdateView):
    model = Kundenauftrag
    form_class = KundenauftragForm
    template_name = 'app_auelb/kundenauftrag_bearbeiten.html'

    def form_valid(self, form):
        self.object = form.save(commit=False)
        if 'foto' in self.request.FILES:
            self.object.foto = self.request.FILES['foto']
        self.object.save()

        # Statuslogik
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
        # Name angepasst an Ihre urls.py
        base_url = reverse('kundenauftrag_bearbeiten', kwargs={'pk': self.object.pk}) 
        params = self.request.GET.urlencode()
        return f"{base_url}?{params}" if params else base_url


# ------------------------------
# Kundenauftrag Update (Formset) - Optimiert
# ------------------------------
@login_required
def kundenauftragUpdate(request, pk):
    # Kundenauftrag holen
    kundenauftrag = get_object_or_404(Kundenauftrag, pk=pk)
    
    # Hole alle Produkte des Kundenauftrags (Verwenden des related_name aus models.py)
    products = kundenauftrag.order_back_1.all()
    
    # --- KORREKTE FORMSET-INITIALISIERUNG MIT form_kwargs ---
    # Dies übergibt den User an die __init__ Methoden in forms.py
    form_kwargs = {'user': request.user}

    if request.method == "POST":
        # Bei POST: data, instance, queryset und form_kwargs übergeben
        formset = Kd_formset(request.POST, instance=kundenauftrag, queryset=products, form_kwargs=form_kwargs)
    else:
        # Bei GET: Nur instance, queryset und form_kwargs übergeben
        formset = Kd_formset(instance=kundenauftrag, queryset=products, form_kwargs=form_kwargs)
    # --- ENDE KORREKTE INITIALISIERUNG ---

    # Debugging-Ausgabe (kann bleiben)
    print(f"Kundenauftrag enthält {products.count()} Produkte.")
    print(f"Anzahl der Form-Instanzen im Formset: {len(formset.forms)}")
    for i, form in enumerate(formset.forms):
        print(f"Form {i} - Instanz ID: {form.instance.id if form.instance else 'None'}")

    # Benutzerrechte prüfen (nur für die POST-Logik benötigt)
    user_groups = [g.name for g in request.user.groups.all()]
    can_edit = "TVK" in user_groups or "PPS_MAWI" in user_groups

    # Die manuelle Deaktivierungslogik in der View ist nun ÜBERFLÜSSIG
    # und wurde entfernt. Die Logik liegt in forms.py.
    readonly_fields = [] # Kann leer bleiben

    # Speichern, wenn POST und Berechtigungen stimmen
    if request.method == "POST" and can_edit and formset.is_valid():
        # Die manuelle Speicherung sorgt für Robustheit
        instances = formset.save(commit=False)
        for instance in instances:
            instance.kundenauftrag = kundenauftrag
            instance.save()
        
        print(f"Formset gespeichert für Kundenauftrag {kundenauftrag.id}")
        
        # Umleitung nach dem Speichern (Post/Redirect/Get Muster)
        query_params = request.GET.copy()
        query_params.pop('from', None)
        query_string = query_params.urlencode()
        
        # Verwenden Sie den korrekten URL-Namen 'kundenauftrag_bearbeiten' aus urls.py
        redirect_url = reverse('kundenauftrag_update', kwargs={'pk': kundenauftrag.pk})

        if query_string:
            return redirect(f"{redirect_url}?{query_string}")
        else:
            return redirect(redirect_url)

    # Bestimmen der "Zurück"-URL
    from_param = request.GET.get("from", "produktiv").lower()
    if from_param == "archiv":
        back_url = reverse("auftragsliste_geliefert")
        back_label = "ARCHIV"
    else:
        back_url = reverse("auftragsliste_nicht_geliefert")
        back_label = "PRODUKTIV"

    # Kontext für das Template
    context = {
        'kundenauftrag': kundenauftrag,
        'formset': formset,
        'can_edit': can_edit,
        'readonly_fields': readonly_fields,
        'back_url': back_url,
        'back_label': back_label,
        'query_string': request.GET.urlencode(),
        'mode_label': "KUNDENAUFTRAG",
        'user_name': request.user.username,
    }

    return render(request, 'app_auelb/auftrag_auffrischen.html', context)

# ------------------------------
# Produkt Update (Formset)
# ------------------------------
@login_required
def produktUpdate(request, pk):
    produkt = get_object_or_404(Produkt, pk=pk)

    # Formset erzeugen und user weitergeben, damit __init__ der Form User kennt
    formset = Prod_formset(request.POST or None, instance=produkt, form_kwargs={'user': request.user})

    # Berechtigungen
    user_groups = [g.name for g in request.user.groups.all()]
    can_edit = "TVK" in user_groups or "PPS_MAWI" in user_groups

    # Readonly-Felder für TVK definieren
    readonly_fields = []
    restricted_fields = ['bezeichnung', 'k_auftragsmenge', 'k_fertigungsauftrag',
                         'k_endtermin', 'k_infofeld', 'statuskomponente']

    if "TVK" in user_groups:
        readonly_fields = restricted_fields

        # Felder direkt in jedem Form deaktivieren
        for form in formset.forms:
            for field_name in restricted_fields:
                if field_name in form.fields:
                    form.fields[field_name].disabled = True
                    form.fields[field_name].required = False

    # Zurück-URL bestimmen
    from_param = request.GET.get("from", "produktiv").lower()
    if from_param == "archiv":
        back_url = reverse("auftragsliste_geliefert")
        back_label = "ARCHIV"
    else:
        back_url = reverse("auftragsliste_nicht_geliefert")
        back_label = "PRODUKTIV"

    query_params = request.GET.copy() or request.POST.copy()
    query_string = query_params.urlencode()

    # Speichern, wenn erlaubt
    if request.method == "POST" and can_edit and formset.is_valid():
        formset.save()
        base_url = reverse('produkt_update', kwargs={'pk': produkt.pk})
        return redirect(f"{base_url}?{query_string}" if query_string else base_url)

    # Kontext für Template
    context = {
        'produkt': produkt,
        'formset': formset,
        'can_edit': can_edit,
        'readonly_fields': readonly_fields,
        'back_url': back_url,
        'back_label': back_label,
        'query_string': query_string,
        'mode_label': "KOMPONENTE",
        'user_name': request.user.username,
    }

    return render(request, 'app_auelb/auftrag_auffrischen_1.html', context)


# ------------------------------
# Komponenten Update
# ------------------------------
@login_required
def komponenten_update(request, produkt_pk):
    produkt = get_object_or_404(Produkt, pk=produkt_pk)
    
    # Hole alle Komponenten dieses Produkts
    komponenten_qs = produkt.order_back_2.all() 

    # --- KORREKTE FORMSET-INITIALISIERUNG MIT form_kwargs ---
    form_kwargs = {'user': request.user}

    if request.method == "POST":
        # Bei POST: data, instance, queryset und form_kwargs übergeben
        formset = Prod_formset(request.POST, instance=produkt, queryset=komponenten_qs, form_kwargs=form_kwargs)
    else:
        # Bei GET: Nur instance, queryset und form_kwargs übergeben
        formset = Prod_formset(instance=produkt, queryset=komponenten_qs, form_kwargs=form_kwargs)
    # --- ENDE KORREKTE INITIALISIERUNG ---

    # Berechtigungen
    user_groups = [g.name for g in request.user.groups.all()]
    # can_edit steuert, ob der "Speichern" Button angezeigt wird und ob die POST-Logik läuft
    can_edit = "PPS_MAWI" in user_groups 

    # Die manuelle Logik zur Deaktivierung der Felder wird HIER ENTFERNT.
    # Sie liegt bereits in der KomponenteForm.__init__ in forms.py

    # Speichern, wenn erlaubt
    if request.method == "POST" and can_edit and formset.is_valid():
        # Die manuelle Speicherung für Robustheit
        instances = formset.save(commit=False)
        for instance in instances:
            instance.product = produkt # Stellen Sie sicher, dass die FK-Beziehung gesetzt ist
            instance.save()
            
        print(f"Komponenten-Formset gespeichert für Produkt {produkt.id}")

        # PRG Muster: Redirect zurück zur selben Seite, um das Formular zurückzusetzen (extra=1)
        return redirect('komponenten_update', produkt_pk=produkt.pk)

    context = {
        'produkt': produkt,
        'formset': formset,
        'can_edit': can_edit,
        'readonly_fields': [], # Leer lassen, die Logik liegt in forms.py
        'user_name': request.user.username,
        'mode_label': "KOMPONENTEN"
    }

    return render(request, 'app_auelb/auftrag_auffrischen_1.html', context)



# ------------------------------
# Merkmale bearbeiten
# ------------------------------
@login_required
def merkmale_bearbeiten(request, pk):
    material = get_object_or_404(Material, pk=pk)
    obj, _ = Merkmale.objects.get_or_create(materialnummer=material)

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


# ------------------------------
# Urblatt bearbeiten
# ------------------------------
@login_required
def urblatt_bearbeiten(request, pk):
    material = get_object_or_404(Material, pk=pk)
    obj, _ = Urblatt.objects.get_or_create(materialnummer=material)

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


# ------------------------------
# Kundenauftrag neu
# ------------------------------
@login_required
def create_kundenauftrag(request):
    can_edit, _ = user_can_edit(request.user)
    if not can_edit:
        return redirect('auftragsliste_nicht_geliefert')

    if request.method == 'POST':
        form = KundenauftragForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('auftragsliste_nicht_geliefert')
    else:
        form = KundenauftragForm()
    return render(request, 'app_auelb/auftrag_neu.html', {'form': form})


# ------------------------------
# KD-Auftragsliste (optional)
# ------------------------------
@login_required
def kd_auftragsliste_view(request):
    theirdata = Kundenauftrag.objects.all()
    if 'searchsuche' in request.GET:
        searchsuche = request.GET['searchsuche']
        if 'my_select' in request.GET:
            my_select = request.GET['my_select']
            theirdata = Kundenauftrag.objects.filter(statuskundenauftrag=my_select).filter(kundenauftrag__icontains=searchsuche)
            if my_select == "1":
                theirdata = Kundenauftrag.objects.filter(kundenauftrag__icontains=searchsuche)

    return render(request, 'app_auelb/auftrag_kd_auftragsliste.html', {
        'meine_daten': Komponente.objects.all(),
        'deine_daten': Produkt.objects.all(),
        'ihre_daten': theirdata,
        'data': StatusKundenauftrag.objects.all(),
    })

# ------------------------
# Benutzergruppenbeispiele erstellen (nur einmalig)
# ------------------------
def create_user_groups():
    groups = ["TVK", "PPS_MAWI", "Produktion"]
    for g in groups:
        Group.objects.get_or_create(name=g)

def create_test_users():
    """
    Benutzer einmalig anlegen mit Passwort:
    TVK -> TVK12345
    PPS_MAWI -> PPS_MAWI1234
    Produktion -> Produktion1234
  
    """
    users = [
        ("TVK", "TVK12345"),
        ("PPS_MAWI", "PPS_MAWI1234"),
        ("Produktion", "Produktion1234"),
       
    ]
    for username, password in users:
        user, created = User.objects.get_or_create(username=username)
        if created:
            user.set_password(password)
            user.save()
            # Gruppe zuweisen
            group = Group.objects.get(name=username)
            user.groups.add(group)
            user.save()

    