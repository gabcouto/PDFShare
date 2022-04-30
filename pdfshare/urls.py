from django.conf.urls.static import static
from django.urls import path, include
from django.views.generic import TemplateView

import projeto.settings
from . import views

urlpatterns = [
    path('', TemplateView.as_view(template_name='home.html'), name='home'),  # Esta é a página inicial.
    path('search/', views.file_list, name='url_file_list'),  # Página que exibe arquivos disponíveis para a compra.
    path('update_compra/<int:pk_comprador>/<int:pk_dono>/<int:pk_produto>/<int:valor_debitado>/', views.update_compra,
         name='url_update_compra'),  # Página serve para atualizar dados no banco quando for efetuada compra.
    path('conta/', include("django.contrib.auth.urls")),
    path('save_file/', views.save_file, name='url_save_file'),  # Pagina que salva arquivos
    path('comprados/', views.files_owned, name='url_files_owned'),
    path('files_saved/', views.files_saved, name='url_files_saved'),  # Pagina arquivos salvos
    path('remove_file/<int:pk_produto>/', views.remove_file, name='url_remove_file'),
    path('edit_file/<int:pk_pdf>/', views.edit_file, name='url_edit_file'),
]

if projeto.settings.DEBUG:
    urlpatterns += static(projeto.settings.MEDIA_URL, document_root=projeto.settings.MEDIA_ROOT)