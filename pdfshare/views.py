import os

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_protect

from .models import *

ADMIN_ID = 1
TAM_MAX = 10000
TAM_MIN = 200


# Esta view exibe lista de arquivos PDF disponíveis para compra.
@login_required
@csrf_protect
def file_list(request):
    files = {}

    # Criamos estes booleanos para evitar uma sequência de nested ifs mais complexa ainda.
    arquivoEnota = request.POST.get('search-type', False) == "arquivo" and request.POST.get('search-order',
                                                                                            False) == "nota"
    arquivoErelevancia = request.POST.get('search-type', False) == "arquivo" and request.POST.get('search-order',
                                                                                                  False) == "relevancia"
    usuarioEnota = request.POST.get('search-type', False) == "usuario" and request.POST.get('search-order',
                                                                                            False) == "nota"
    usuarioErelevancia = request.POST.get('search-type', False) == "usuario" and request.POST.get('search-order',
                                                                                                  False) == "relevancia"
    espacovazio = request.POST.get('caixa-pesquisa', False) == ""

    if arquivoEnota:
        if espacovazio:
            files = PDF.objects.all().order_by('-nota')
        else:
            files = PDF.objects.filter(filename=request.POST.get('caixa-pesquisa', False)).order_by('-nota')
    elif arquivoErelevancia:
        if espacovazio:
            files = PDF.objects.all().order_by('-quantidadeNota')
        else:
            files = PDF.objects.filter(filename=request.POST.get('caixa-pesquisa', False)).order_by('-quantidadeNota')
    elif usuarioEnota:
        if espacovazio:
            files = PDF.objects.all().order_by('-nota')
        else:
            files = PDF.objects.filter(
                fileauthor__user__username__contains=request.POST.get('caixa-pesquisa', False)).order_by('-nota')
    elif usuarioErelevancia:
        if espacovazio:
            files = PDF.objects.all().order_by('-quantidadeNota')
        else:
            files = PDF.objects.filter(
                fileauthor__user__username__contains=request.POST.get('caixa-pesquisa', False)).order_by(
                '-quantidadeNota')
    else:
        files = PDF.objects.all().order_by('-nota')
    return render(request, 'filelist.html', {'files': files, 'searchtype': request.POST.get('search-type', False),
                                             'searchorder': request.POST.get('search-order', False)})


@login_required
# Esta view tem como funcionalidade atualizar dados no banco quando for efetuada compra.
def update_compra(request, pk_comprador, pk_dono, pk_produto, valor_debitado):
    usuario_comprador = Usuario.objects.get(pk=pk_comprador)
    usuario_dono = Usuario.objects.get(pk=pk_dono)
    produto_comprado = PDF.objects.get(pk=pk_produto)

    if (usuario_comprador.pontuacao < valor_debitado):
        messages.error(request,
                       'Não possui saldo para efetuar a compra')  # nao exibe a mensagem de erro por que redireciona para outra pagina
        return redirect('url_file_list')
    elif usuario_comprador == usuario_dono:
        messages.error(request, 'Você é o proprietário desse pdf')
        return redirect('url_file_list')
    elif Transacao.objects.filter(produto__pk=pk_produto, comprador__pk=pk_comprador):
        messages.error(request, 'Você ja possui esse pdf')
        return redirect('url_file_list')

    usuario_comprador.pontuacao -= valor_debitado
    usuario_dono.pontuacao += valor_debitado
    transacao = Transacao(produto=produto_comprado, comprador=usuario_comprador, preco=valor_debitado)

    difference_days =abs((usuario_comprador.user.last_login - usuario_comprador.last_login).days)
    if difference_days > 1:
        usuario_comprador.last_login = usuario_comprador.user.last_login
        usuario_comprador.download_count = 0
    elif usuario_comprador.download_count >= 5:
        messages.error(request, 'Você ja adquiriu 5 pdfs hoje')
        return redirect('url_file_list')

    usuario_comprador.increment_download_count()

    usuario_comprador.save()
    usuario_dono.save()
    transacao.save()

    return redirect('url_file_list')


# Esta view exibe os PDFs comprados por um determinado usuário.
@login_required
def files_owned(request):
    files = {}
    usuario = Usuario.objects.get(user__id=request.user.id)
    # Somente exibimos os arquivos dos usuários que não estão devendo pontos.
    if usuario.pontuacao >= 0:
        files = Transacao.objects.filter(comprador__pk=usuario.id)
    return render(request, 'filesowned.html', {'files': files})


@login_required
def files_saved(request):
    files = {}
    usuario = Usuario.objects.get(user__id=request.user.id)
    # Somente exibimos os arquivos dos usuários que não estão devendo pontos.
    files = PDF.objects.filter(fileauthor__pk=usuario.id)
    return render(request, 'filessaved.html', {'files': files})


# Esta view tem como funcionalidade remover dados no banco.
@login_required
def remove_file(request, pk_produto):
    # Resgatamos dados do banco a partir das primary keys fornecidas.
    produto = PDF.objects.get(pk=pk_produto)
    usuario_dono = produto.fileauthor

    for transaction in Transacao.objects.filter(produto__pk=pk_produto):
        if transaction.preco != 0:
            usuario_dono.pontuacao -= transaction.preco
        usuario_dono.save()
        transaction.comprador.pontuacao += transaction.preco
        transaction.comprador.save()
        transaction.delete()

    # Apagamos o arquivo dos nossos diretórios:
    if os.path.isfile(produto.filepath.path):
        os.remove(produto.filepath.path)
    # Por fim, apagamos a entrada do banco:
    produto.delete()
    # Este return deve estar com esta identação. É o return do def, e não do if acima.
    return redirect('url_files_saved')


@login_required
def save_file(request):
    if request.method != 'POST':
        form = FormPdf()
        return render(request, 'savefile.html', {'form': form})
    form = FormPdf(request.POST, request.FILES)
    if len(request.FILES.dict()) != 0:

        if not 'PDF' in request.FILES['filepath'].name.upper():
            messages.error(request, 'Arquivo não é do tipo PDF')
            form = FormPdf(request.POST)
            return render(request, 'savefile.html', {'form': form})

        filesize = request.FILES['filepath'].size / 1024
        form = FormPdf(request.POST)
        if filesize < TAM_MIN:
            messages.error(request, 'Arquivo menor que 200Kbs')
            return render(request, 'savefile.html', {'form': form})
        elif filesize > TAM_MAX:
            messages.error(request, 'Arquivo maior que 10000Kbs')
            return render(request, 'savefile.html', {'form': form})

        if form.is_valid():
            form = FormPdf(request.POST, request.FILES)
            new_form = form.save(commit=False)
            ownerPdf = new_form.fileauthor.id
            add_points(ownerPdf)
            aux_filesize = request.FILES['filepath'].size
            new_form.filesize = aux_filesize / 1024
            if new_form.fileauthor.id != ADMIN_ID:
                new_form.status = 'd'
            new_form.save()
            return redirect('url_file_list')
    messages.error(request, 'Faça upload do arquivo')
    return render(request, 'savefile.html', {'form': form})


def add_points(ownerPdfId):
    owner = Usuario.objects.get(pk=ownerPdfId)
    owner.pontuacao += 15
    owner.save()


@login_required()
def edit_file(request, pk_pdf):
    pdf = PDF.objects.get(pk=pk_pdf)
    form = FormEditPdf(instance=pdf)

    if request.method == 'POST':
        form = FormEditPdf(request.POST, request.FILES, instance=pdf)

        if not 'PDF' in request.FILES['filepath'].name.upper():
            messages.error(request, 'Arquivo não é do tipo PDF')
            form = FormEditPdf(request.POST, instance=pdf)
            return render(request, 'editfile.html', {'form': form})

        filesize = request.FILES['filepath'].size / 1024
        form = FormEditPdf(request.POST)
        if filesize < TAM_MIN:
            messages.error(request, 'Arquivo menor que 200Kbs')
            return render(request, 'editfile.html', {'form': form})
        elif filesize > TAM_MAX:
            messages.error(request, 'Arquivo maior que 10000Kbs')
            return render(request, 'editfile.html', {'form': form})

        if form.is_valid():
            form.save()
            return redirect('url_file_list')

    return render(request, 'editfile.html', {'form': form})
