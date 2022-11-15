from django.db import models


class bill_data(models.Model):
    bill_type = models.CharField(max_length=30)
    bill_id = models.CharField(max_length=200)
    price = models.IntegerField(null=True)
    bill_period = models.CharField(max_length=100)
    entity = models.CharField(max_length=30)
    reference = models.CharField(max_length=30)
    limit_date = models.DateField('limit date')

    def __str__(self):
        return self.bill_id
    