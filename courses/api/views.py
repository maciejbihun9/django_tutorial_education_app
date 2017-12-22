from rest_framework import generics
from ..models import Subject
from .serializers import SubjectSerializer
from .serializers import CourseSerializer
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authentication import BasicAuthentication
from rest_framework.permissions import IsAuthenticated
from ..models import Course
from rest_framework import viewsets
from rest_framework.decorators import detail_route
from .serializers import CourseSerializer
from .permissions import IsEnrolled
from .serializers import CourseWithContentsSerializer

# Widoki są potrzebne tylko do zwrócenia danych w ładnym formacie
# Jest to taki dodatek, tylko aby móc sobie to ładnie wyświetlić w przeglądarce,
# obiekt javaScript JSON by to odebrał normalnie ;)
class SubjectListView(generics.ListAPIView):
    """
    View - odnosi się do tego, że możemy zwrócić dane
    w widoku django_rest w postaci JSON.
    """
    # pobranie obiektów
    queryset = Subject.objects.all()
    # metoda do serializacji obiektów przed zwróceniem
    serializer_class = SubjectSerializer

# pobieranie widoków szczegółych obiektu
# RetrieveAPIView - wie o istnieniu atrybutu pk.
class SubjectDetailView(generics.RetrieveAPIView):
    """
    RetrieveAPIView - Used for read-only endpoints to
     represent a single model instance.
    """
    # pobranie obiektów
    queryset = Subject.objects.all()
    # metoda do serializacji obiektów
    serializer_class = SubjectSerializer

# dobra metoda do postowania zasobów z innych aplikacji.
class CourseEnrollView(APIView):
    """
    * APIView dobrze zabezpieczas zasoby, ale działa tak jak View
    * Różnica między klasami APIView i View polega na tym, że
    pierwsza z wymienionych korzysta z obiektów Request i Response frameworka REST oraz
    zapewnia obsługę wyjątków APIException zwracających odpowiednie odpowiedzi HTTP.
    * Widok CourseEnrollView obsługuje zapisanie się użytkownika na kursy.
    """
    # dane autentykacji będą perzesłane za pomocą url
    authentication_classes = (BasicAuthentication,)
    # anonimowi nie mają dostępu do danych
    permission_classes = (IsAuthenticated,)
    # żadna inna metoda nie może otrzymać dostępu do tego widoku.
    def post(self, request, pk, format=None):
        course = get_object_or_404(Course, pk=pk)
        # Dodanie bieżącego użytkownika do związku students typu „wiele do wielu”
        course.students.add(request.user)
        # użytkownik po żądaniu dostaje wiadomość
        return Response({'enrolled': True})

class CourseViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Dostarcza akcje tylko do odczytu. read() oraz retrive()
    """
    queryset = Course.objects.all()
    serializer_class = CourseSerializer

class CourseViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Dostarcza akcje tylko do odczytu: list(), retrive()
    """
    queryset = Course.objects.all()
    serializer_class = CourseSerializer

    # przedstawia dodatkowe akcje dla danej kolekcji widoku.
    # @detail_route - określenie, że akcje będzie wykonana na pojedyńczym obiekcie.
    # teraz metoda ta oczekuje parametru id w url żądania, ten url jest podany do pobrania
    # obiekt z get_object()
    # tylko metoda post jest możliwa oraz
    # dodajemy klasy uprawnień oraz uwierzytelnienia
    @detail_route(methods=['post'],
                  authentication_classes=[BasicAuthentication],
                  permission_classes=[IsAuthenticated])
    def enroll(self, request, *args, **kwargs):
        # parametr pk podany w url pobrał nam obiekt.
        course = self.get_object()
        # dodanie user do związku "wiele do wielu"
        course.students.add(request.user)
        return Response({'enrolled': True})

    # @detail_route - deklaracja, że akcja jest na pojedeyńczym obiekcie,
    # tylko metoda get jest dozwolona,
    # CourseWithContentsSerializer - uwzględnia wygenerowana treść kursu,
    @detail_route(methods=['get'],
                  serializer_class=CourseWithContentsSerializer,
                  authentication_classes=[BasicAuthentication],
                  # tylko zalogowany użytkownik ma dostęp
                  permission_classes=[IsAuthenticated, IsEnrolled])
    # nazwa tej metody pojawia się w url zarządzanym przez router.
    def contents(self, request, *args, **kwargs):
        """
        * Pozwala na zwrócenie całości danych powiązanych z danym kursem
        Zostało to zadeklarowane w metodach serializacji kursu

        * Dla podanego url: api/courses/1/contents/
        - pk = 1
        - nazwa metody contents
        - mając serializer można było pobrać odpowiedni kurs w klasie Serializer
        - póxniej kaskadowo dociągano dane i wywołano metodę do zwrócenia zawartości.
        """
        return self.retrieve(request, *args, **kwargs)
