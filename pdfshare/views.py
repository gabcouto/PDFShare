import os

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

from .models import *

# Esta view exibe lista de arquivos PDF disponíveis para compra.
ADMIN_ID = 1
TAM_MAX = 10000
TAM_MIN = 200


def file_list(request):
    # TODO: Não exibir mais as que o usuário já comprou
    current_user = request.user.id
    transacoes=Transacao.objects.filter(comprador__pk=current_user)

    files = PDF.objects.all()
    return render(request, 'filelist.html', {'files': files})


def save_file(request):
    if request.method != 'POST':
        form = FormPdf()
        return render(request, 'savefile.html', {'form': form})
    form = FormPdf(request.POST, request.FILES)

    if not 'PDF' in request.FILES['filepath'].name.upper():
        messages.error(request, 'Arquivo não é do tipo PDF')
        form = FormPdf(request.POST)
        return render(request, 'savefile.html', {'form': form})

    filesize = len(request.FILES['filepath'].read()) / 1000
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

def add_points(ownerPdfId):
    owner = Usuario.objects.get(pk=ownerPdfId)
    owner.pontuacao += 15
    owner.save()


@login_required
def files_owned(request):
    files = {}
    usuario = Usuario.objects.get(user__id=request.user.id)
    # Somente exibimos os arquivos dos usuários que não estão devendo pontos.
    if usuario.pontuacao >= 0:
        files = Transacao.objects.filter(comprador__pk=usuario.id)
    return render(request, 'filesowned.html', {'files': files})


@login_required
def my_files(request):
    files = {}
    usuario = Usuario.objects.get(user__id=request.user.id)
    # Somente exibimos os arquivos dos usuários que não estão devendo pontos.
    files = PDF.objects.filter(fileauthor__pk=usuario.id)
    return render(request, 'myfiles.html', {'files': files})


@login_required()
def edit_file(request, pk_pdf):
    pdf = PDF.objects.get(pk=pk_pdf)
    form = FormEditPdf(instance=pdf)

    if request.method =='POST':
        form = FormEditPdf(request.POST, request.FILES, instance=pdf)

        if not 'PDF' in request.FILES['filepath'].name.upper():
            messages.error(request, 'Arquivo não é do tipo PDF')
            form = FormEditPdf(request.POST, instance=pdf)
            return render(request, 'editfile.html', {'form': form})

        if form.is_valid():
            form.save()
            return redirect('url_file_list')

    return render(request, 'editfile.html', {'form': form})


# Esta view tem como funcionalidade remover dados no banco.
@login_required
def remove_file(request, pk_produto):
    # Resgatamos dados do banco a partir das primary keys fornecidas.
    produto = PDF.objects.get(pk=pk_produto)
    usuario_dono = produto.fileauthor

    for transaction in Transacao.objects.filter(produto__pk=pk_produto):
        usuario_dono.pontuacao -= transaction.preco
        usuario_dono.save()
        transaction.comprador.pontuacao += transaction.preco
        transaction.comprador.save()
        transaction.delete()

    # Apagamos o arquivo dos nossos diretórios:
    if os.path.isfile(produto.filepath + produto.filename):
        os.remove(produto.filepath + produto.filename)
    # Por fim, apagamos a entrada do banco:
    produto.delete()
    # Este return deve estar com esta identação. É o return do def, e não do if acima.
    return redirect('url_files_saved')
