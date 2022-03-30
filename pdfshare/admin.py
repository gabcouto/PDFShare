from django.contrib import admin
from .models import *


# Para que os modelos criados sejam exibidos na pagina localhost:8000/admin, é necessário cadastrá-los aqui:
admin.site.register(PDF)
admin.site.register(Usuario)
admin.site.register(Transacao)