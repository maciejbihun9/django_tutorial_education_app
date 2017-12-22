from django import forms
from courses.models import Course

class CourseEnrollForm(forms.Form):
    """
    Ten formularz wykorzystamy, aby umożliwić uczestnikom zapisywanie się na kursy.
    """

    # Pole course wskazuje kurs, na który jest zapisany dany użytkownik.
    # W formularzu inicjalizujemy ukryte pole przez umieszczenie
    # w nim bieżącego obiektu Course, aby mógł zostać wysłany bezpośrednio.
    # queryset - pobiera wszystkie kursy jako parametry
    course = forms.ModelChoiceField(queryset=Course.objects.all(),
                                    widget=forms.HiddenInput)


