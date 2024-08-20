from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response

from api.v1.permissions import IsStudentOrIsAdmin, ReadOnlyOrIsAdmin, make_payment
from api.v1.serializers.course_serializer import (CourseSerializer,
                                                  CreateCourseSerializer,
                                                  CreateGroupSerializer,
                                                  CreateLessonSerializer,
                                                  GroupSerializer,
                                                  LessonSerializer)
from api.v1.serializers.user_serializer import SubscriptionSerializer
from courses.models import Course, Group
from users.models import Balance, CustomUser, Subscription


class LessonViewSet(viewsets.ModelViewSet):
    """Уроки."""

    permission_classes = (IsStudentOrIsAdmin,)

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return LessonSerializer
        return CreateLessonSerializer

    def perform_create(self, serializer):
        course = get_object_or_404(Course, id=self.kwargs.get('course_id'))
        serializer.save(course=course)

    def get_queryset(self):
        course = get_object_or_404(Course, id=self.kwargs.get('course_id'))
        return course.lessons.all()


class GroupViewSet(viewsets.ModelViewSet):
    """Группы."""

    permission_classes = (permissions.IsAdminUser,)

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return GroupSerializer
        return CreateGroupSerializer

    def perform_create(self, serializer):
        course = get_object_or_404(Course, id=self.kwargs.get('course_id'))
        serializer.save(course=course)

    def get_queryset(self):
        course = get_object_or_404(Course, id=self.kwargs.get('course_id'))
        return course.group.all()


class CourseViewSet(viewsets.ModelViewSet):
    """Курсы """

    queryset = Course.objects.all()
    permission_classes = (ReadOnlyOrIsAdmin,)

    # def get_queryset(self):
    #     user = self.request.user
    #     if user.is_authenticated:
    #         if self.action == 'list':
    #             return Course.objects.exclude(id__in=user.courses.values_list('id', flat=True))
    #     return Course.objects.all()

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return CourseSerializer
        return CreateCourseSerializer

    def retrieve(self, request, *args, **kwargs):
        """Получение информации о курсе."""
        user = request.user
        course = self.get_object()

        if not user.is_authenticated:
            return Response(
                data={"message": "Необходимо войти в систему для доступа к этому курсу."},
                status=status.HTTP_401_UNAUTHORIZED
            )

        if course not in user.courses.all() and not user.is_staff and not user.is_superuser:
            return Response(
                data={"message": "У вас нет доступа к этому курсу."},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = self.get_serializer(course)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        """Создание нового курса с автоматическим созданием групп."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        course = serializer.save()

        groups = []
        for i in range(1, 11):
            group = Group(
                title=f'Группа №{i}',
                course=course
            )
            groups.append(group)
        
        Group.objects.bulk_create(groups)

        return Response(serializer.data, status=status.HTTP_201_CREATED)


    @action(
        methods=['post'],
        detail=True,
        permission_classes=(permissions.IsAuthenticated,)
    )
    def pay(self, request, pk):
        """Покупка доступа к курсу (подписка на курс)."""

        query_course = Course.objects.filter(id=pk)
        if len(query_course)==0:
            return Response(
                data={"message": "Курс не найден."},
                status=status.HTTP_404_NOT_FOUND
            )
        course = query_course[0]
        user = self.request.user
        if course in user.courses.all():
            return Response(
                data={"message": "Курс уже куплен на вашем аккаунте."},
                status=status.HTTP_200_OK
            )

        return make_payment(request=request,
                    pk=pk,
                    course=course,
                    user=user
                    )
    
    @action(
        methods=['get'],
        detail=False,
        permission_classes=(permissions.IsAuthenticated,)
    )
    def forbuy(self, request):
        """Получение курсов, rкоторые пользователь не покупал."""
        user = request.user
        queryset = Course.objects.exclude(id__in=user.courses.values_list('id', flat=True))
        serializer = CourseSerializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(
        methods=['get'],
        detail=False,
        permission_classes=(permissions.IsAuthenticated,)
    )
    def groups(self, request, pk):
        """Получение групп курса."""
        course = get_object_or_404(Course, id=pk)
        serializer = GroupSerializer(course.group.all(), many=True) 
        return Response(serializer.data)