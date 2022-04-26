from datetime import datetime

from django import forms
from django.contrib.auth.models import User
from django.core.validators import FileExtensionValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from projeto.settings import BASE_DIR


class Usuario(models.Model):
    # Nós precisamos usar a classe User do Django, mas ela não pode ser alterada. Contudo, nós precisamos que o usuário tenha o parâmetro 'pontuacao'. Por isso, criamos um modelo 'Usuario' que possui um parâmetro 'User'.
    user = models.OneToOneField(User, on_delete=models.CASCADE) # TODO: revisar se o 'CASCADE' é apropriado.
    pontuacao = models.IntegerField(null=True)
    download_count = models.PositiveIntegerField(default=0, blank=False,null=False)
    last_login = models.DateTimeField(default=datetime.strptime('2022-04-01', '%Y-%m-%d'))
    # TODO: Já há alguns 'usertypes' padrão. Podemos utilizá-los?
    # Isto serve apenas para melhor visualização dos dados no Shell do Django. Ignorem.

    def increment_download_count(self):
        self.download_count += 1

    def __str__(self):
        return self.user.username

class PDF(models.Model):
    STATUS_CHOICES = [
        ('d', 'Draft'),
        ('p', 'Published'),
    ]
    filename = models.CharField(max_length=100)
    fileauthor = models.ForeignKey(Usuario, on_delete=models.RESTRICT, null=True) # TODO: garantir que se eu excluir um arquivo eu nao exclua o usuario; mas nao o contrario.
    nota = models.IntegerField(default=0)
    quantidadeNota = models.IntegerField(default=0)
    filepath=models.FileField(upload_to=BASE_DIR.__str__()+"/pdfs",
                     validators=[FileExtensionValidator(['pdf'])],
                              blank=True,
                              null=True,)
    filesize = models.IntegerField(default=0)
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default='p')
    def __str__(self):
        return self.filename

class Transacao(models.Model):
    # Toda transação possui um produto e um comprador. Esta classe é necessária.
    produto = models.ForeignKey(PDF, on_delete=models.RESTRICT, null=True)
    comprador = models.ForeignKey(Usuario, on_delete=models.RESTRICT, null=True)
    preco = models.IntegerField(null=True)

class FormPdf(forms.ModelForm):
    class Meta:
        model = PDF
        fields=('filename','fileauthor' ,'filepath')
        labels = {
            'filename': _('Titulo'),
            'fileauthor': _('Criado Por'),
            'filepath': _('Arquivo'),
        }
class FormEditPdf(forms.ModelForm):
    class Meta:
        model = PDF
        fields=('filename','filepath')
        labels = {
            'filename': _('Titulo'),
            'filepath': _('Arquivo'),
        }