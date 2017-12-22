from rest_framework.permissions import BasePermission

class IsEnrolled(BasePermission):

    # sprawdzamy, czy user znajduje się w związku students, aby pokazać mu odpowiednie treści
    def has_object_permission(self, request, view, obj):
        return obj.students.filter(id=request.user.id).exists()

