from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from .fields import OrderField
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe

class Subject(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)

    class Meta:
        ordering = ('title',)

    def __str__(self):
        return self.title

class Course(models.Model):
    owner = models.ForeignKey(User, related_name='courses_created')
    subject = models.ForeignKey(Subject, related_name='courses')
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    overview = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    # studenci mogą być na wielu kursach oraz kursy mogą mieć wiele studentów
    # poprzez courses_joined można dotrzeć do tego
    # na jakie kursy jest zapisany dany uzytkownik.
    students = models.ManyToManyField(User,
                                      related_name='courses_joined',
                                      blank=True)

    class Meta:
        ordering = ('-created',)

    def __str__(self):
        return self.title

class Module(models.Model):
    course = models.ForeignKey(Course, related_name='modules')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    # kolejność ma zostać ustalona z uwzględnieniem kursu.
    order = OrderField(blank=True, for_fields=['course'], null=True)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return '{}. {}'.format(self.order, self.title)

class Content(models.Model):
    # Moduł może zawierać różnorodną treść, więc definiujemy kolumnę typu
    # ForeignKey prowadzącą do modelu Module.
    module = models.ForeignKey(Module, related_name='contents')
    order = OrderField(blank=True, for_fields=['module'], null=True)
    # wskazująca w modelu kolumnę typu ContentType.
    # wskazanie jakie modele mogą być tutaj dodane jako content type.
    content_type = models.ForeignKey(ContentType,
                                     limit_choices_to={'model__in': ('text',
                                                                     'video',
                                                                     'image',
                                                                     'file')})
    # przeznaczona do przechowywania klucza podstawowego powiązanego obiektu.
    object_id = models.PositiveIntegerField()
    # prowadząca do powiązanego obiektu przez połączenie dwóch poprzednich kolumn.
    item = GenericForeignKey('content_type', 'object_id')

    class Meta:
        ordering = ['order']

class ItemBase(models.Model):
    # Django pozwala na określenie miejsca zarezerwowanego dla nazwy klasy modelu
    # User będzie posiadał wiele ItemBasów różnego typu
    owner = models.ForeignKey(User, related_name='%(class)s_related')
    title = models.CharField(max_length=250)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

    def __str__(self):
        return self.title

    # dostarcza interfejs przeznaczony do generowania różnorodnej treści.
    def render(self):
        # celu wygenerowania szablonu, a następnie
        # przygotowaną treść zwraca w postaci ciągu tekstowego.
        return render_to_string('courses/content/{}.html'.format(
            # do przygotowania odpowiedniego szablonu
            self._meta.model_name), {'item': self})

class Text(ItemBase):
    content = models.TextField()

class File(ItemBase):
    file = models.FileField(upload_to='files')

class Image(ItemBase):
    file = models.FileField(upload_to='images')

class Video(ItemBase):
    url = models.URLField()