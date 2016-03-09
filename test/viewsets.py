from rest_framework import viewsets

from .serializers import PersonSerializer, AccountSerializer, ComputerSerializer

class Base(viewsets.ModelViewSet):
    def get_queryset(self):
        return self.model.objects.all()

class PersonViewSet(Base):
    model = PersonSerializer.Meta.model
    serializer_class = PersonSerializer

class AccountViewSet(Base):
    model = AccountSerializer.Meta.model
    serializer_class = AccountSerializer

class ComputerViewSet(Base):
    model = ComputerSerializer.Meta.model
    serializer_class = ComputerSerializer
