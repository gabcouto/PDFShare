from django.urls import path, include
from django.views.generic import TemplateView

from . import views

urlpatterns = [
    path('', TemplateView.as_view(template_name='home.html'), name='home'),  # Esta é a página inicial.
    path('search/', views.file_list, name='url_file_list'),  # Página que exibe arquivos disponíveis para a compra.
    path('update_compra/<int:pk_comprador>/<int:pk_dono>/<int:pk_produto>/<int:valor_debitado>/', views.update_compra,
         name='url_update_compra'),  # Página serve para atualizar dados no banco quando for efetuada compra.
    path('conta/', include("django.contrib.auth.urls")),
    path('save_file/', views.save_file, name='url_files_saved'),  # Pagina que salva arquivos
    path('my_files/', views.my_files, name='url_my_files'),  # Pagina arquivos salvos
    path('remove_file/<int:pk_produto>/', views.remove_file, name='url_remove_file'),
    path('edit_file/<int:pk_pdf>/', views.edit_file, name='url_edit_file')
]
