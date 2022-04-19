import os.path

from django.core.validators import FileExtensionValidator
from django.db import models
from django import forms
from django.utils.translation import gettext_lazy as _

# Create your models here.

from django.contrib.auth.models import User

from projeto.settings import BASE_DIR


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
    nota = models.IntegerField(default=0)
    quantidadeNota = models.IntegerField(default=0)
    filepath=models.FileField(upload_to='images\\trabalho ESN',
                     validators=[FileExtensionValidator(['pdf'])],
                              blank=True,
                              null=True,)
    filesize = models.IntegerField(default=0)
    def __str__(self):
        return self.filename

class Transacao(models.Model):
    # Toda transação possui um produto e um comprador. Esta classe é necessária.
    produto = models.ForeignKey(PDF, on_delete=models.RESTRICT, null=True)
    comprador = models.ForeignKey(Usuario, on_delete=models.RESTRICT, null=True)

class FormContato(forms.ModelForm):
    class Meta:
        model = PDF
        fields=('filename','fileauthor' ,'filepath')
        labels = {
            'filename': _('Titulo'),
            'fileauthor': _('Criado Por'),
            'filepath': _('Arquivo'),
        }