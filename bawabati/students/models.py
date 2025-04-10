from django.db import models
from courses.models import Classe
# Create your models here.


class Eleve(models.Model):
    nom = models.CharField(max_length=100, unique=True) 
    prenom = models.CharField(max_length=100, unique=True) 
    date_naissance = models.DateField()
    email = models.EmailField(unique=True, max_length=100)
    classe = models.ForeignKey(Classe, on_delete=models.CASCADE, related_name='eleves')

    def __str__(self):
        return f"{self.prenom} {self.nom}"