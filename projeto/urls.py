"""projeto URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from pdfshare import views
from django.views.generic.base import TemplateView

urlpatterns = [
    path('admin/', admin.site.urls), # Página de admin.
    path('', TemplateView.as_view(template_name='home.html'), name='home'), # Esta é a página inicial.
    path('search/', views.file_list, name='url_file_list'), # Página que exibe arquivos disponíveis para a compra.
    path('update_compra/<int:pk_comprador>/<int:pk_dono>/<int:pk_produto>/<int:valor_debitado>/', views.update_compra, name='url_update_compra'), # Página serve para atualizar dados no banco quando for efetuada compra. 
    path('conta/', include("django.contrib.auth.urls")),
    path('comprados/<int:pk_comprador>/', views.files_owned, name='url_files_owned'),
]
