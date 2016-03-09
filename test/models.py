from django.utils.timezone import now
from django.db import models

class Base(models.Model):
    class Meta:
        abstract = True

class Person(Base):
    name = models.CharField(max_length=255, null=True, blank=True)
    age = models.IntegerField(default=18, null=True, blank=True)
    created = models.DateTimeField(null=True, blank=True, default=now)

    computers = models.ManyToManyField('test.Computer', null=True, blank=True)
    account = models.ForeignKey('test.Account', null=True, blank=True)

class Computer(Base):
    name = models.CharField(max_length=255, null=True, blank=True)

class Account(Base):
    name = models.CharField(max_length=255, null=True, blank=True)
