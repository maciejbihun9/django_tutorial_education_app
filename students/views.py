from django.core.urlresolvers import reverse_lazy
from django.views.generic.edit import CreateView
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login
from django.views.generic.edit import FormView
from braces.views import LoginRequiredMixin
from .forms import CourseEnrollForm
from django.views.generic.list import ListView
from courses.models import Course
from django.views.generic.detail import DetailView

class StudentRegistrationView(CreateView):
    """
    Jest to widok pozwalający na rejestrację uczestników.
    """

    template_name = 'students/student/registration.html'
    # Oferowany przez Django UserCreationForm wykorzystujemy jako formularz
    # do budowania obiektów User.
    form_class = UserCreationForm
    # Adres URL, na który użytkownik zostanie przekierowany po pomyślnym
    # wysłaniu formularza.
    success_url = reverse_lazy('student_course_list')

    # Metoda form_valid() jest wykonywana po przekazaniu prawidłowych danych formularza.
    # Wartością zwrotną tej metody jest odpowiedź HTTP.
    # Nadpisujemy tę metodę w celu zalogowania użytkownika po udanej rejestracji.
    def form_valid(self, form):
        result = super(StudentRegistrationView,
                       self).form_valid(form)

        cd = form.cleaned_data
        user = authenticate(username=cd['username'],
                            password=cd['password1'])
        login(self.request, user)
        return result

class StudentEnrollCourseView(LoginRequiredMixin, FormView):
    """
    * Jest to widok StudentEnrollCourseView odpowiedzialny
    za obsługę zapisu uczestników na kursy.
    * Widok dziedziczy po domieszce LoginRequiredMixin, aby tylko zalogowany użytkownik
    mógł uzyskać do niego dostęp.
    * FormView - ponieważ obsługujemy operację wysłania formularza.
    """
    # przechowuje dany obiekt course
    course = None
    form_class = CourseEnrollForm

    def form_valid(self, form):
        # jeśli dane są dobre to zapisujemy danego user'a do studentów kursu.
        self.course = form.cleaned_data['course']
        self.course.students.add(self.request.user)
        return super(StudentEnrollCourseView, self).form_valid(form)

    # Metoda get_success_url() zwraca adres URL,
    # do którego użytkownik zostanie przekierowany
    # po udanym wysłaniu formularza.
    # Metoda jest odpowiednikiem atrybutu success_url.
    def get_success_url(self):
        return reverse_lazy('student_course_detail', args=[self.course.id])


class StudentCourseListView(LoginRequiredMixin, ListView):
    """
    * LoginRequiredMixin - zapewnia, że tylko zalogowani mogą się tutaj dostać,
    * Widok ten jest przeznaczony dla uczestników
    i wyświetla kursy, na które się zapisali,
    * Jak wyświetlać liste jakiś obiektów, to tylko extends ListView
    """
    model = Course
    template_name = 'students/course/list.html'
    def get_queryset(self):
        """
        * metoda zostaje nadpisana, aby pobraćtylko te obiektu, na które
        zapisał się użytkownik.
        """
        qs = super(StudentCourseListView, self).get_queryset()
        return qs.filter(students__in=[self.request.user])

class StudentCourseDetailView(DetailView):
    model = Course
    template_name = 'students/course/detail.html'

    def get_queryset(self):
        """
        * pobieranie obiektów wskazanego typu.
        """
        qs = super(StudentCourseDetailView, self).get_queryset()
        return qs.filter(students__in=[self.request.user])

    def get_context_data(self, **kwargs):
        """
        * kwargs - są to parametry adresu url w postaci zbioru.
        * aby wybrać moduł kursu i podać go w kontekście,
        jeśli wprowadzony został parametr adresu URL o nazwie module_id.
        """
        context = super(StudentCourseDetailView,
                        self).get_context_data(**kwargs)
        # Pobranie obiektu kursu.
        # metoda get_object pobiera dane z url po podaniu ściśle określonych nazw
        # a adresie url: id, pk, slug. Sprawdź jakie klucze są podawane do zbioru podczas
        # wyciągania wartości zanim zbudujesz url.
        course = self.get_object()
        if 'module_id' in self.kwargs:
            # Pobranie bieżącego modułu i dodanie go do kontekstu.
            # W ten sposób uczestnik ma możliwość poruszania się po modułach
            # wewnątrz kursu.
            context['module'] = course.modules.get(
                                id=self.kwargs['module_id'])
        else:
            # Pobranie pierwszego modułu.
            context['module'] = course.modules.all()[0]
        return context
