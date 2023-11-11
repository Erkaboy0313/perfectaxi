from django.db import models as db_models

# Create your models here.

class TaskCount(db_models.Model):
    name = db_models.CharField(max_length=200,blank=True)
    count = db_models.IntegerField(default=0)

    def __str__(self):
        return f"{self.name} - {self.count}"
