from django.db import models
from django import forms

# Create your models here.

from django.contrib.auth.models import User


class Usuario(models.Model):
    # Nós precisamos usar a classe User do Django, mas ela não pode ser alterada. Contudo, nós precisamos que o usuário tenha o parâmetro 'pontuacao'. Por isso, criamos um modelo 'Usuario' que possui um parâmetro 'User'.
    user = models.OneToOneField(User, on_delete=models.CASCADE) # TODO: revisar se o 'CASCADE' é apropriado.
    pontuacao = models.IntegerField(null=True)
    # TODO: Já há alguns 'usertypes' padrão. Podemos utilizá-los?
    # Isto serve apenas para melhor visualização dos dados no Shell do Django. Ignorem.
    def __str__(self):
        return self.user.username

class PDF(models.Model):
    filename = models.CharField(max_length=100)
    fileauthor = models.ForeignKey(Usuario, on_delete=models.RESTRICT, null=True) # TODO: garantir que se eu excluir um arquivo eu nao exclua o usuario; mas nao o contrario.
    filesize = models.IntegerField(null=True)
    nota = models.IntegerField(default=0) # colocar valor padrao 0
    quantidadeNota = models.IntegerField(default=0) # colocar valor padrao 0
    filepath = models.CharField(max_length=250, null=True) # TODO: Deveria estar null=True?
    def __str__(self):
        return self.filename

class Transacao(models.Model):
    # Toda transação possui um produto e um comprador. Esta classe é necessária.
    produto = models.ForeignKey(PDF, on_delete=models.RESTRICT, null=True)
    comprador = models.ForeignKey(Usuario, on_delete=models.RESTRICT, null=True)

class FormContato(forms.ModelForm):
    class Meta:
        model = PDF
        exclude=('quantidadeNota', 'nota',)