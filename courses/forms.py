from django import forms
from django.forms.models import inlineformset_factory
from .models import Course, Module

# Wymieniona funkcja pozwala na dynamiczne utworzenie modelu zbioru formularzy
# dla obiektów Module powiązanych z obiektami Course.
# Podczas edytowania wszystkie moduły podpięte wcześniej pod Course są wyświetlane.
ModuleFormSet = inlineformset_factory(Course,
                                    Module,
                                      # pola w formie
                                    fields=['title',
                                    'description'],
                                    # dodatkowe formy pod już istniejącymi
                                    extra=2,
                                    # pole wyboru do usunięcia (thick)
                                    can_delete=True)
