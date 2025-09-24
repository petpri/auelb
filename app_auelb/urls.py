from django.urls import path
from . import views

urlpatterns = [
    # ------------------------
    # Auftragslisten
    # ------------------------
    path('auftraege/nicht-geliefert/', views.auftragsliste_nicht_geliefert_view, name='auftragsliste_nicht_geliefert'),
    path('auftraege/geliefert/', views.auftragsliste_geliefert_view, name='auftragsliste_geliefert'),

    # ------------------------
    # Kundenauftrag
    # ------------------------
    path('kundenauftrag/neu/', views.create_kundenauftrag, name='create_kundenauftrag'),
    path('kundenauftrag/bearbeiten/<int:pk>/', views.KundenauftragUpdate.as_view(), name='kundenauftrag_bearbeiten'),
    path('kundenauftrag/update/<int:pk>/', views.kundenauftragUpdate, name='kundenauftrag_update'),

    # ------------------------
    # Produkt
    # ------------------------
    path('produkt/update/<int:pk>/', views.produktUpdate, name='produkt_update'),

    # ------------------------
    # Merkmale
    # ------------------------
    path('merkmale/update/<int:pk>/', views.MerkmaleUpdate.as_view(), name='merkmale_bearbeiten'),

    # ------------------------
    # Urblatt
    # ------------------------
    path('urblatt/update/<int:pk>/', views.UrblattUpdate.as_view(), name='urblatt_bearbeiten'),

    # ------------------------
    # Kundenauftragsliste (optional)
    # ------------------------
    path('kd_auftragsliste/', views.kd_auftragsliste_view, name='kd_auftragsliste'),
]
