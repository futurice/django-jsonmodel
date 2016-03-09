from .models import Person, Computer, Account

from rest_framework import serializers

class Base(serializers.ModelSerializer):
    pass

class PersonSerializer(Base):
    class Meta:
        model = Person

class AccountSerializer(Base):
    class Meta:
        model = Account

class ComputerSerializer(Base):
    class Meta:
        model = Computer
