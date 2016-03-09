from .models import Person, Computer

from rest_framework import serializers

class Base(serializers.ModelSerializer):
    pass

class PersonSerializer(Base):

    class Meta:
        model = Person
