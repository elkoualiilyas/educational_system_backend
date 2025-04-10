from django.contrib import admin

# Register your models here.pytho
from django.contrib import admin
from .models import Note

@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
    list_display = ('eleve', 'cours', 'note', 'date_ajout')
    list_filter = ('cours', 'eleve')
    search_fields = ('eleve__nom', 'eleve__prenom', 'cours__nom')
