from django.urls import path,include
from .views import auftragsliste_view, create_kundenauftrag, kundenauftragUpdate, produktUpdate, KundenauftragUpdate, kd_auftragsliste_view

urlpatterns=[
    path('auftragsliste/', auftragsliste_view, name='auftrag_auftragsliste'),
    path('kundenauftrag_bearbeiten/<int:pk>/', KundenauftragUpdate.as_view(), name='kundenauftrag_bearbeiten'),
    path('neu/', create_kundenauftrag, name='auftrag_neu'),
    path('auffrischen/<int:pk>/', kundenauftragUpdate, name='auftrag_auffrischen'),
    path('auffrischen_1/<int:pk>/', produktUpdate, name='auftrag_auffrischen_1'), 
    path('kd_auftragsliste/', kd_auftragsliste_view, name='auftrag_kd_auftragsliste'),
    path("select2/", include("django_select2.urls")),
    
]