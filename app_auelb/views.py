from django.contrib.auth.decorators import login_required
from django.views.generic import UpdateView
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.db.models import Q
from .models import (
    Kundenauftrag, Produkt, Komponente, StatusKundenauftrag,
    StatusProdukt, Kunde, Material, Merkmale, Urblatt, StatusKomponente
)
from .forms import KundenauftragForm, Kd_formset, Prod_formset, MerkmaleForm, UrblattForm,KomponenteForm
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
            Q(order_back_1__bezeichnung__materialnummer__icontains=materials)
            | Q(order_back_1__order_back_2__bezeichnung__materialnummer__icontains=materials)
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
            Q(order_back_1__bezeichnung__materialnummer__icontains=materials)
            | Q(order_back_1__order_back_2__bezeichnung__materialnummer__icontains=materials)
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
        base_url = reverse('kundenauftrag_bearbeiten', kwargs={'pk': self.object.pk})
        params = self.request.GET.urlencode()
        return f"{base_url}?{params}" if params else base_url


# ------------------------------
# Kundenauftrag Update (Formset)
# ------------------------------
@login_required
def kundenauftragUpdate(request, pk):
    kundenauftrag = get_object_or_404(Kundenauftrag, pk=pk)
    formset = Kd_formset(request.POST or None, instance=kundenauftrag)

    # Bestimmen der "Zurück"-URL
    from_param = request.GET.get("from", "produktiv").lower()
    if from_param == "archiv":
        back_url = reverse("auftragsliste_geliefert")
        back_label = "ARCHIV"
    else:
        back_url = reverse("auftragsliste_nicht_geliefert")
        back_label = "PRODUKTIV"

    # Aktuelle Query-Parameter
    query_params = request.GET.copy() or request.POST.copy()
    query_string = query_params.urlencode()

    # Benutzerrechte
    user_groups = [g.name for g in request.user.groups.all()]
    can_edit = "TVK" in user_groups or "PPS_MAWI" in user_groups

    # Felder, die TVK nur lesen darf
    readonly_fields = []
    restricted_fields = ["p_kalkpreis", "p_serviceanfrage", "p_endtermin", "p_fertigungsauftrag"]

    if "TVK" in user_groups:
        readonly_fields = restricted_fields

        # Felder direkt im Formset deaktivieren
        for form in formset.forms:
            for field_name in restricted_fields:
                if field_name in form.fields:
                    form.fields[field_name].disabled = True
                    form.fields[field_name].required = False  # optional, damit Speichern klappt

    # Felder, die Produktion nur lesen darf
    readonly_fields = []
    restricted_fields = ["p_kalkpreis", "p_serviceanfrage", "p_endtermin", "p_fertigungsauftrag","bezeichnung","p_auftragsmenge","p_endtermin_wunsch"]

    if "Produktion" in user_groups:
        readonly_fields = restricted_fields

        # Felder direkt im Formset deaktivieren
        for form in formset.forms:
            for field_name in restricted_fields:
                if field_name in form.fields:
                    form.fields[field_name].disabled = True
                    form.fields[field_name].required = False  # optional, damit Speichern klappt

    # Speichern, wenn POST und erlaubt
    if request.method == "POST" and can_edit and formset.is_valid():
        formset.save()
        if query_string:
            return redirect(f"{reverse('kundenauftrag_update', kwargs={'pk': kundenauftrag.pk})}?{query_string}")
        else:
            return redirect(reverse('kundenauftrag_update', kwargs={'pk': kundenauftrag.pk}))

    # Kontext für Template
    context = {
        'kundenauftrag': kundenauftrag,
        'formset': formset,
        'can_edit': can_edit,
        'readonly_fields': readonly_fields,
        'back_url': back_url,
        'back_label': back_label,
        'query_string': query_string,
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

# ------------------------
# Komponenten update
# ------------------------
@login_required
def komponenten_update(request, produkt_pk):
    produkt = get_object_or_404(Produkt, pk=produkt_pk)
    formset = Prod_formset(request.POST or None, instance=produkt, user=request.user)

    # Berechtigungen
    user_groups = [g.name for g in request.user.groups.all()]
    can_edit = "PPS_MAWI" in user_groups  # nur PPS darf editieren

    # Readonly-Felder definieren
    readonly_fields = []
    if "TVK" in user_groups or "Produktion" in user_groups or "Meister" in user_groups:
        readonly_fields = [
            'bezeichnung', 'k_auftragsmenge', 'k_fertigungsauftrag',
            'k_endtermin', 'k_infofeld', 'statuskomponente'
        ]

        # Felder direkt im Formset deaktivieren
        for form in formset.forms:
            for field_name in readonly_fields:
                if field_name in form.fields:
                    form.fields[field_name].disabled = True
                    form.fields[field_name].required = False

    # Speichern, wenn erlaubt
    if request.method == "POST" and can_edit and formset.is_valid():
        formset.save()
        # optional: redirect zurück
        return redirect('kundenauftrag_update', pk=produkt.kundenauftrag.pk)

    context = {
        'produkt': produkt,
        'formset': formset,
        'can_edit': can_edit,
        'readonly_fields': readonly_fields,
        'user_name': request.user.username,
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

    