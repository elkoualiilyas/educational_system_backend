from django.contrib import admin

# Register your models here.
from .models import Professeur

@admin.register(Professeur)
class ProfesseurAdmin(admin.ModelAdmin):
    list_display = ('prenom', 'nom', 'matiere', 'email')
    search_fields = ('prenom', 'nom', 'matiere')