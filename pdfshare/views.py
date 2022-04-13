from django.shortcuts import render, redirect
from .models import *
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_protect

# Esta view exibe lista de arquivos PDF disponíveis para compra.
@login_required
@csrf_protect
def file_list(request): 
    files = {}

    # Criamos estes booleanos para evitar uma sequência de nested ifs mais complexa ainda.
    arquivoEnota = request.POST.get('search-type', False) == "arquivo" and request.POST.get('search-order', False) == "nota"
    arquivoErelevancia = request.POST.get('search-type', False) == "arquivo" and request.POST.get('search-order', False) == "relevancia"
    usuarioEnota = request.POST.get('search-type', False) == "usuario" and request.POST.get('search-order', False) == "nota"
    usuarioErelevancia = request.POST.get('search-type', False) == "usuario" and request.POST.get('search-order', False) == "relevancia"
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
            files = PDF.objects.filter(fileauthor__user__username__contains=request.POST.get('caixa-pesquisa', False)).order_by('-nota')
    elif usuarioErelevancia:
        if espacovazio:
            files = PDF.objects.all().order_by('-quantidadeNota')
        else:
            files = PDF.objects.filter(fileauthor__user__username__contains=request.POST.get('caixa-pesquisa', False)).order_by('-quantidadeNota')
    else:
        files = PDF.objects.all().order_by('-nota')

    return render(request, 'filelist.html', {'files': files, 'searchtype': request.POST.get('search-type', False), 'searchorder': request.POST.get('search-order', False)})

# Esta view tem como funcionalidade atualizar dados no banco quando for efetuada compra.
@login_required
def update_compra(request, pk_comprador, pk_dono, pk_produto, valor_debitado):
    # Resgatamos dados do banco a partir das primary keys fornecidas.
    usuario_comprador = Usuario.objects.get(pk=pk_comprador)
    usuario_dono = Usuario.objects.get(pk=pk_dono)
    produto_comprado = PDF.objects.get(pk=pk_produto)
    # Verificamos se o cara tem saldo, mas não informamos se não tem. (TODO)
    # Impedimos de comprar novamente, mas não avisamos (TODO)
    if (usuario_comprador.pontuacao >= valor_debitado) and (usuario_comprador != usuario_dono) and not Transacao.objects.filter(produto__pk=pk_produto, comprador__pk=pk_comprador):
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

# Esta view exibe os PDFs comprados por um determinado usuário.
@login_required
def files_owned(request):
    files = {}
    usuario = Usuario.objects.get(user__id=request.user.id)
    # Somente exibimos os arquivos dos usuários que não estão devendo pontos.
    if usuario.pontuacao >= 0:
        files = Transacao.objects.filter(comprador__pk=usuario.id)
    return render(request, 'filesowned.html', {'files': files})

