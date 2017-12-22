from rest_framework import serializers
from ..models import Subject
from ..models import Course
from ..models import Content
from ..models import Module

# ModelSerializer - Zapewnia obsługę serializacji dla egzemplarzy klas modelu.
# klasa models -> JSON format object
class SubjectSerializer(serializers.ModelSerializer):
    """
    W jaki sposób serializować podany obiekt.
    Jest to serializacja dla modelu Subject.
    """

    class Meta:
        """
        Klasa Meta pozwala na wskazanie modelu przeznaczonego do serializacji,
        a także kolumn, które mają być uwzględnione w trakcie tego procesu.
        """
        model = Subject
        fields = ('id', 'title', 'slug')

class ModuleSerializer(serializers.ModelSerializer):
    """
    W jaki sposób serializować klasę Module.
    """
    class Meta:
        model = Module
        fields = ('order', 'title', 'description')

class CourseSerializer(serializers.ModelSerializer):
    # w celu zapewnienia serializacji modelu Module.
    # wskazujemy na serializacjęwielu obiektów
    # kolumna jest tylko do odczytu i nie powinna być uwzględniana
    # w jakichkolwiek danych
    # wejściowych podczas tworzenia lub uaktualniania obiektów.
    modules = ModuleSerializer(many=True, read_only=True)

    class Meta:
        model = Course
        fields = ('id', 'subject', 'title', 'slug', 'overview',
                  'created', 'owner', 'modules')

# wygenerowanie własnej kolumny
class ItemRelatedField(serializers.RelatedField):

    def to_representation(self, value):
        return value.render()

class ContentSerializer(serializers.ModelSerializer):
    # tworzenie własnej kolumny
    item = ItemRelatedField(read_only=True)
    class Meta:
        model = Content
        fields = ('order', 'item')


class ModuleWithContentsSerializer(serializers.ModelSerializer):
    contents = ContentSerializer(many=True)
    class Meta:
        model = Module
        fields = ('order', 'title', 'description', 'contents')

class CourseWithContentsSerializer(serializers.ModelSerializer):
    modules = ModuleWithContentsSerializer(many=True)

    class Meta:
        model = Course
        fields = ('id', 'subject', 'title', 'slug',
        'overview', 'created', 'owner', 'modules')

