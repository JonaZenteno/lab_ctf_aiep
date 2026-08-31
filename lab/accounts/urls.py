from django.urls import path

from . import views

urlpatterns = [
    path("retos/", views.hub_view, name="hub"),
    path("comprobar-flag/", views.comprobar_flag_view, name="comprobar_flag"),
    path("login/", views.login_view, name="login"),
    path("reto3/", views.reto3_view, name="reto3"),
    path("transferir/", views.transferir_fondos, name="transferir_fondos"),
    path("buscar/", views.buscar_view, name="buscar"),
    path("verificar/", views.verificar_view, name="verificar"),
]
