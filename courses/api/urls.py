from django.conf.urls import url
from . import views
from django.conf.urls import url, include
from rest_framework import routers
from . import views

# router staje się odpowiedzialny za automatyczne
# generowanie adresów URL dla kolekcji widoku.
router = routers.DefaultRouter()
# zarejestrowaliśmy kolekcję widoku wraz z prefiksem courses.
router.register('courses', views.CourseViewSet)

urlpatterns = [
    url(r'^subject/(?P<pk>\d+)/$',
        views.SubjectDetailView.as_view(),
        name='subject_detail'),

    url(r'^subjects/$',
        views.SubjectListView.as_view(),
        name='subject_list'),

    url(r'^', include(router.urls)),
]