from django.core.urlresolvers import reverse_lazy
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from braces.views import LoginRequiredMixin, PermissionRequiredMixin
from django.shortcuts import redirect, get_object_or_404
from django.views.generic.base import TemplateResponseMixin, View
from .forms import ModuleFormSet
from .models import Course
from django.shortcuts import render
from django.forms.models import modelform_factory
from django.apps import apps
from .models import Module, Content
import web_pdb

class ManageCourseListView(ListView):
    model = Course

    template_name = 'courses/manage/course/list.html'

    # metoda query set domyslnie pobiera wszystkie elementy zwiazane z klasą model.
    def get_queryset(self):
        # aby pobierać jedynie kursy utworzone przez bieżącego użytkownika.
        qs = super(ManageCourseListView, self).get_queryset()
        # zwrócenie tylko elementow dla zalogowanego użytkownika.
        return qs.filter(owner=self.request.user)

# DOMIESZKI, CZYLI ZDEFINIOWANIE JAKIŚ DODATKOWYCH FUNKCJONLANOŚCI

class OwnerMixin(object):
    def get_queryset(self):
        # coś tutaj kurwa nie działa
        qs = super(OwnerMixin, self).get_queryset()
        return qs.filter(owner=self.request.user)

class OwnerEditMixin(object):
    # Metoda form_valid() jest wywoływana, gdy wysłany formularz będzie prawidłowy.
    # domyśle działanie to zapisanie ModelForm oraz przekierowanie, ale
    # tutaj następuje nadpisanie, aby przypisać użykownika podczsas zapisywania obiektu
    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super(OwnerEditMixin, self).form_valid(form)

# dostarczającą poniższy atrybut widokom potomnym.
# metoda get_query_set() już tutaj jest,
# to się wykonuje po usunięciu oraz edytowaniu, także tutaj widać przydatność!
class OwnerCourseMixin(OwnerMixin, LoginRequiredMixin):
    model = Course
    fields = ['subject', 'title', 'slug', 'overview']
    # przekierowanie pod zadany url
    success_url = reverse_lazy('manage_course_list')

class OwnerCourseEditMixin(OwnerCourseMixin, OwnerEditMixin):
    # kolumny modelu do utworzenia formularza
    fields = ['subject', 'title', 'slug', 'overview']
    # przekierowanie po udanym wysłaniu
    success_url = reverse_lazy('manage_course_list')
    template_name = 'courses/manage/course/form.html'

class ManageCourseListView(OwnerCourseMixin, ListView):
    template_name = 'courses/manage/course/list.html'

# Domieszka PermissionRequiredMixin sprawdza, czy użytkownik
# uzyskujący dostęp do widoku
# ma uprawnienia wymienione w atrybucie permission_required.
# Używa ModelForm do utworzenia nowego obiektu Course.
# jak nie ma tych uprawnień to nie wejdzie na stronke
class CourseCreateView(PermissionRequiredMixin, OwnerCourseEditMixin, CreateView):
    permission_required = 'courses.add_course'

# Pozwala na edycję istniejącego obiektu Course.
class CourseUpdateView(OwnerCourseEditMixin, UpdateView):
    permission_required = 'courses.change_course'
    pass

# Definiuje success_url w celu przekierowania
# użytkownika pod podany adres URL po usunięciu obiektu.
class CourseDeleteView(OwnerCourseMixin, DeleteView):
    template_name = 'courses/manage/course/delete.html'
    success_url = reverse_lazy('manage_course_list')
    permission_required = 'courses.delete_course'

# TemplateResponseMixin - Domieszka jest odpowiedzialna za wygenerowanie szablonów
# i zwrot odpowiedzi HTTP.
# View - Dostarczany przez Django podstawowy widok oparty na klasie.
class CourseModuleUpdateView(TemplateResponseMixin, View):
    template_name = 'courses/manage/module/formset.html'

    course = None

    # Definiujemy tę metodę, aby uniknąć powielania kodu
    # odpowiedzialnego za utworzenie zbioru formularzy.
    def get_formset(self, data=None):
        # utworzenie formsetu dla obiektu rodzinca course
        return ModuleFormSet(instance=self.course, data=data)

    # ogólnie próbuje delegoważ żądania do get lub post
    # kiedy się to wywołuje? - podczas żądania http, więć jest pierwszą, która się wywoła
    # ta metoda może nam inicjalizować jakieś obiekty. Pobiera żądanie, więc ma dostęp do parametrów ządania.
    # warto ją nadpisać aby mieć dodatkową funkcjonalność widoku podczas inicjaliacji
    # metoda ta również zwraca odpowiedź
    # metoda dispatch próbuje delegować żądania do metod get() oraz post(), czyli metody get oraz set
    # muszą być implementowane, bo inaczej widok nie zadziała
    def dispatch(self, request, pk):
        # przypisane obiektu do pola publicznego
        self.course = get_object_or_404(Course,
                                        id=pk,
                                        owner=request.user)

        # wywołąnie metody wyżej położonej
        return super(CourseModuleUpdateView, self).dispatch(request, pk)

    def get(self, request, *args, **kwargs):
        # tworzenie pustego obiektu formset
        formset = self.get_formset()
        # zbudowanie formy wraz z obiektem Course
        return self.render_to_response({'course': self.course,
                                    'formset': formset})

    def post(self, request, *args, **kwargs):
        # zbudowanie formy w zależności od tego co było w POST
        formset = self.get_formset(data=request.POST)

        # walidacja wszystkich form na raz.
        # jeśli nie, następuje wygenerowanie szablonu wraz z odpowiednimi komunikatami błędów.
        if formset.is_valid():
            # zapisanie wszystkich form do bazki
            formset.save()
            return redirect('manage_course_list')
        # przekazanie szablonu do kontekstu i jego generacja
        return self.render_to_response({'course': self.course,
                                    'formset': formset})


class ContentCreateUpdateView(TemplateResponseMixin, View):
    module = None
    model = None
    obj = None
    template_name = 'courses/manage/content/form.html'

    # pobranie klasy modelu podanej jako parametr
    def get_model(self, model_name):
        if model_name in ['text', 'video', 'image', 'file']:
            # pobranie rzeczywistej klasy dla danej nazwy modelu.
            return apps.get_model(app_label='courses', model_name=model_name)
        return None

    def get_form(self, model, *args, **kwargs):
        # my robimy forme dla text, video, image, file
        # dynamiczne budowanie formularza wraz ze wskazaniem pól do wykluczenia,
        # bo pozostałe są dołączone automatycznie.
        # w tym przypadku dołączamy tylko pliki
        Form = modelform_factory(model, exclude=['owner',
                                                'order',
                                                'created',
                                                'updated'])
        return Form(*args, **kwargs)

    def dispatch(self, request, module_id, model_name, id=None):
        # przychodzi żądanie, pobieramy moduł
        self.module = get_object_or_404(Module, id=module_id, course__owner=request.user)
        # model name przychodzi z żądaniem, dlatego wiadomo co tutaj pobrać
        self.model = self.get_model(model_name)
        if id:
            self.obj = get_object_or_404(self.model,
                                                id=id,
                                                owner=request.user)
        return super(ContentCreateUpdateView,
            self).dispatch(request, module_id, model_name, id)

    def get(self, request, module_id, model_name, id=None):
        # tworzenie formy dla podanego modelu(jest globalną zmienną
        # inicjalizowaną podczas żądania.
        form = self.get_form(self.model, instance=self.obj)
        return self.render_to_response({'form': form, 'object': self.obj})

    def post(self, request, module_id, model_name, id=None):
        # tutaj już wszystko mamy, bo jesteśmy w widoku i wysyłamy jego zawartość
        # dlatego trzeba jeszcze raz zbudować formę, aby ją zwalidować.
        form = self.get_form(self.model,
                             instance=self.obj,
                             data=request.POST,
                             files=request.FILES)

        if form.is_valid():
            obj = form.save(commit=False)
            obj.owner = request.user
            obj.save()
            if not id:
                # Nowa treść.
                Content.objects.create(module=self.module, item=obj)
            return redirect('module_content_list', self.module.id)
        return self.render_to_response({'form': form, 'object': self.obj})

# to jest widok, który po wykonaniu posta na formie przekierowuje na podany url.
# ta klasa posiada przypisany template, ale nie jest nie podany
class ContentDeleteView(View):

    # metoda post jest wywoływana przez metodę dispatch klasy View, gdy
    # okaże się, że jest to metoda po wysłaniu post'a
    def post(self, request, id):
        content = get_object_or_404(Content,
                                    id=id,
                                    module__course__owner=request.user)
        # usuwanie powiązanych obiektów
        # czyli nie ma tutaj usuwania eager, czyli całości za jednym razem.
        module = content.module
        content.item.delete()
        content.delete()
        return redirect('module_content_list', module.id)

# ten widok jest zwracany tylko i wyłącznie pod zadany url dla metody get()
# po każdym wywołaniu tej metody z url który również znajduje sie w template tego widoku
# następuje wywołanie tej funkcji(czyli ponowna komunikacja z serwerem)
# po każdym naciśnięciu widok jest renderowany ponownie.
# fajny sposób, aby zrobić takie menu, ale to nie jest ajaxowe, bo zwracana jest cała strona, czyli jest
# w chuj procesowania
class ModuleContentListView(TemplateResponseMixin, View):
    template_name = 'courses/manage/module/content_list.html'

    def get(self, request, module_id):
        module = get_object_or_404(Module, id=module_id, course__owner=request.user)
        # nie udostępnia żądania w odpowiedzi(obiektu żądania, czyli nie ma użytkownika.
        # render to response też może przyjmować parametry (html template)
        # może wrzucić tam request poprzez: context_instance=RequestContext(request)
        # Always use render and not render_to_response
        # render to response nie posiada: user, csrf_token, and messages.
        return self.render_to_response({'module': module})




