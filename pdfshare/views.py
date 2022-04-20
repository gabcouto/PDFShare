from django.contrib import messages
from django.shortcuts import render, redirect

from .models import *


# Esta view exibe lista de arquivos PDF disponíveis para compra.
def file_list(request):
    # TODO: Não exibir mais as que o usuário já comprou
    files = {}
    # Resgatamos todos os arquivos PDF do banco e retornamos.
    files = PDF.objects.all()
    return render(request, 'filelist.html', {'files': files})


def save_file(request):
    if request.method != 'POST':
        form = FormContato()
        return render(request, 'savefile.html', {'form': form})
    form = FormContato(request.POST, request.FILES)

    if not 'PDF' in request.FILES['filepath'].name.upper():
        messages.error(request, 'Arquivo não é do tipo PDF')
        form = FormContato(request.POST)
        return render(request, 'savefile.html', {'form': form})

    filesize = len(request.FILES['filepath'].read()) / 1000
    form = FormContato(request.POST)
    if filesize < 200:
        messages.error(request, 'Arquivo menor que 200Kbs')
        return render(request, 'savefile.html', {'form': form})
    elif filesize > 10000:
        messages.error(request, 'Arquivo maior que 10000Kbs')
        return render(request, 'savefile.html', {'form': form})

    if form.is_valid():
        form = FormContato(request.POST, request.FILES)
        new_form = form.save(commit=False)
        ownerPdf = new_form.fileauthor.id
        add_points(ownerPdf)
        aux_filesize = request.FILES['filepath'].read()
        new_form.filesize = len(aux_filesize) / 1000
        new_form.save()
    return redirect('url_save_file')


def add_points(ownerPdfId):
    owner = Usuario.objects.get(pk=ownerPdfId)
    owner.pontuacao += 15
    owner.save()
    redirect('url_save_file')


def valid_filesize(request, filesize):
    if filesize < 200:
        messages.error(request, 'Arquivo menor que 200Kbs')
        return False
    elif filesize > 10000:
        messages.error(request, 'Arquivo maior que 10000Kbs')
        return False
    return True

# Esta view tem como funcionalidade atualizar dados no banco quando for efetuada compra.
def update_compra(request, pk_comprador, pk_dono, pk_produto, valor_debitado):
    # Resgatamos dados do banco a partir das primary keys fornecidas.
    usuario_comprador = Usuario.objects.get(pk=pk_comprador)
    usuario_dono = Usuario.objects.get(pk=pk_dono)
    produto_comprado = PDF.objects.get(pk=pk_produto)
    # Verificamos se o cara tem saldo, mas não informamos se não tem. (TODO)
    # Impedimos de comprar novamente, mas não avisamos (TODO)
    if (usuario_comprador.pontuacao >= valor_debitado) and (
            usuario_comprador != usuario_dono) and not Transacao.objects.filter(produto__pk=pk_produto,
                                                                                comprador__pk=pk_comprador):
        # Debitamos pontuação do comprador; adicionamos pontuação ao dono do arquivo.
        usuario_comprador.pontuacao -= valor_debitado
        usuario_dono.pontuacao += valor_debitado
        # Registramos a transação.
        transacao = Transacao(produto=produto_comprado, comprador=usuario_comprador)
        # Salvamos as alterações no banco.
        usuario_comprador.save()
        usuario_dono.save()
        transacao.save()
    # Este return deve estar com esta identação. É o return do def, e não do if acima.
    return redirect('url_file_list')


def my_files(request, pk_usuario):
    # TODO: Não exibir mais as que o usuário já comprou
    files = {}
    # Resgatamos todos os arquivos PDF do banco e retornamos.
    files = PDF.objects.all()
    return render(request, 'myfiles.html', {'files': files})
