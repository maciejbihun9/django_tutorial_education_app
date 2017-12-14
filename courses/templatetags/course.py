from django import template
register = template.Library()

# filtr szablonu
# W szablonach możemy go zastosować jako
# object|model_name, aby pobrać nazwę modelu dla danego obiektu.
@register.filter
def model_name(obj):
    try:
        return obj._meta.model_name
    except AttributeError:
        return None