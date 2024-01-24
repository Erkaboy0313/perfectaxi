from django.db import models as db_models

# Create your models here.

class TaskCount(db_models.Model):
    name = db_models.CharField(max_length=200,blank=True)
    count = db_models.IntegerField(default=0)

    @property
    def inc(self):
        self.count += 1
        self.save()

    def __str__(self):
        return f"{self.name} - {self.count}"

class SearchRadius(db_models.Model):
    radius1 = db_models.IntegerField(default=1000)
    radius2 = db_models.IntegerField(default=2000)
    radius3 = db_models.IntegerField(default=3000)
    radius4 = db_models.IntegerField(default=5000)

    def __str__(self):
        return f"{self.radius1} - {self.radius2}"