from django.db import models
# Create your models here.


class SpreadSheet(models.Model):
    myId = models.IntegerField()
    name = models.TextField()
    content = models.TextField()
    date = models.DateField()
