from django.contrib import admin

# Register your models here.
from .models import Classe, Cours

@admin.register(Classe)
class ClasseAdmin(admin.ModelAdmin):
    list_display = ('nom', 'niveau')
    search_fields = ('nom', 'niveau')

@admin.register(Cours)
class CoursAdmin(admin.ModelAdmin):
    list_display = ('nom', 'classe', 'professeur')
    list_filter = ('classe', 'professeur')