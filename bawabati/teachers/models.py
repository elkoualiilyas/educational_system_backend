from django.db import models

# Create your models here.
class Professeur(models.Model):
    nom =models.CharField(max_length=100, unique=True) 
    prenom =models.CharField(max_length=100, unique=True) 
    email = models.EmailField(unique=True, max_length=192)
    matiere =models.CharField(max_length=100, unique=True) 

    def __str__(self):
        return f"{self.prenom} {self.nom} - {self.matiere}"
