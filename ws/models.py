from django.db import models

# Create your models here.

class TaskCount(models.Model):
    name = models.CharField(max_length=200,blank=True)
    count = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.name} - {self.count}"