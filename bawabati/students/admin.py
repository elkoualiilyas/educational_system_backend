from django.contrib import admin

# Register your models here.
from .models import Eleve

@admin.register(Eleve)
class EleveAdmin(admin.ModelAdmin):
    list_display = ('prenom', 'nom', 'classe', 'email')
    search_fields = ('prenom', 'nom', 'email')
    list_filter = ('classe',)