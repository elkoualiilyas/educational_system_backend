from django.db import models

# Create your models here.
from students.models import Eleve
from courses.models import Cours

class Note(models.Model):
    eleve = models.ForeignKey(Eleve, on_delete=models.CASCADE)
    cours = models.ForeignKey(Cours, on_delete=models.CASCADE)
    note = models.DecimalField(max_digits=4, decimal_places=2)  # 0.00 to 20.00
    date_ajout = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.eleve} - {self.cours.nom} : {self.note}"
