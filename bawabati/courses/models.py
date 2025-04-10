from django.db import models

# Create your models here.

from teachers.models import Professeur

class Classe(models.Model):
    nom = models.CharField(max_length=20)  # e.g. "2ème année collège"
    niveau = models.CharField(max_length=50)  # e.g. "Collège"

    def __str__(self):
        return self.nom

class Cours(models.Model):
    nom = models.CharField(max_length=100)
    professeur = models.ForeignKey(Professeur, on_delete=models.SET_NULL, null=True)
    classe = models.ForeignKey(Classe, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.nom} ({self.classe})"
