from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import BasePermission, SAFE_METHODS

from users.models import Balance, Subscription
from courses.models import Group


def make_payment(request, pk, course, user):
    course_price = course.price
    user_balance = Balance.objects.get(user=user)
    if user_balance.cash < course_price:
        return Response(
            data={"message": "Недостаточно средств на вашем счету."},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    Balance.objects.filter(id=user_balance.id).update(cash=user_balance.cash-course_price)
    user.courses.add(course)

    groups = Group.objects.filter(course=course.id)
    f = False
    for group in groups:
        if len(group.students.all()) == 30:
            continue
        group.students.add(user)
        f = True
        break
    
    if not f:
        return Response(
            data={"message": "Нет свободных групп для этого курса."},
            status=status.HTTP_400_BAD_REQUEST
        )

    return Response(
        data=request.data,
        status=status.HTTP_201_CREATED
        )


class IsStudentOrIsAdmin(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_authenticated:
            return request.user.courses.exists() 
        
    def has_object_permission(self, request, view, obj):
        if request.user.is_authenticated:
            return obj.course in request.user.courses.all()


class ReadOnlyOrIsAdmin(BasePermission):

    def has_permission(self, request, view):
        return request.user.is_staff or request.method in SAFE_METHODS

    def has_object_permission(self, request, view, obj):
        return request.user.is_staff or request.method in SAFE_METHODS
