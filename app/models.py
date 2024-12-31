from django.db import models


class Person(models.Model):
    fname = models.CharField(max_length=30, null=False)
    cname = models.CharField(max_length=30, null=False)
    qnt = models.IntegerField(null=False)
    price = models.IntegerField(null=False)
    tot = models.IntegerField(null=False)
    date = models.DateField(null=False)

    def __str__(self):
        return self.fname
    
class Accounts(models.Model):
    name = models.CharField(max_length=20, null=False)
    type = models.CharField(max_length=6, null=False)
    balance = models.IntegerField(null=False)
    def __str__(self):
        return self.name
    
class Transactions(models.Model):
    name = models.CharField(max_length=20, null=False)
    type = models.CharField(max_length=6, null=False)
    date = models.DateField(null=False)
    in_amt = models.IntegerField(null=False)
    out_amt = models.IntegerField(null=False)
    ad = models.BooleanField(default=False)
    def __str__(self):
        return self.name

class Pending(models.Model):
    name = models.CharField(max_length=20, null=False)
    date = models.DateField(null=False)
    pending = models.BooleanField(default=True)
    given = models.DateField()
    def __str__(self):
        return self.name

class Submit(models.Model):
    name = models.CharField(max_length=20, null=False)
    date = models.DateField(null=False)
    def __str__(self):
        return self.name