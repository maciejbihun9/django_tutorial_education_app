from django.db import models
from django.core.exceptions import ObjectDoesNotExist


# moja własna kolumna modelu
class OrderField(models.PositiveIntegerField):

    # for_fields pozwalający na wskazanie kolumn, których kolejność należy uwzględnić
    # podczas ustalania kolejności dla danej kolumny.
    def __init__(self, for_fields=None, *args, **kwargs):
        self.for_fields = for_fields
        super(OrderField, self).__init__(*args, **kwargs)

    # metoda wywołana przed umieszczeniem kolumny w bazie danych
    def pre_save(self, model_instance, add):
        if getattr(model_instance, self.attname) is None:
            # Brak bieżącej wartości.
            try:
                qs = self.model.objects.all()
                if self.for_fields:
                    # Filtrowanie względem obiektów o tych samych wartościach kolumny
                    # dla kolumn w "for_fields".
                    query = {field: getattr(model_instance, field) for field in
                    self.for_fields}
                    qs = qs.filter(**query)
                    # Pobranie kolejności ostatniego elementu.
                last_item = qs.latest(self.attname)
                value = last_item.order + 1
            except ObjectDoesNotExist:
                value = 0
            setattr(model_instance, self.attname, value)
            return value
        else:
            return super(OrderField, self).pre_save(model_instance, add)