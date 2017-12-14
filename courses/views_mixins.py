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


# DOMIESZKI, CZYLI ZDEFINIOWANIE JAKIŚ DODATKOWYCH FUNKCJONLANOŚCI DLA KLAS WIDOKÓW


# DOMIESZKI, CZYLI ZDEFINIOWANIE JAKIŚ DODATKOWYCH FUNKCJONLANOŚCI
class OwnerMixin(object):
    def get_queryset(self):
        # coś tutaj kurwa nie działa
        qs = super(OwnerMixin, self).get_queryset()
        return qs.filter(owner=self.request.user)


class OwnerEditMixin(object):
    # metoda form_valid nie posiada swojej funkcjonalności w tym miejscu, ona dziedziczy ją
    # z klasy widoku. Dopiero podczas dziedziczenia ortzyma swoją moc.
    # Jest to bardzo dziwne, bo ta klasa dziedziczy po klasie, która nie posaida żadnej
    # funkcjonalności, ale otrzyma ją później.

    # Ja bym rozważył, czy takie zastosowanie nie jest zbyt niebezpieczne.

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