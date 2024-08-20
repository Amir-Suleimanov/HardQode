from django.contrib.auth import get_user_model
from django.db.models import Avg, Count
from rest_framework import serializers

from courses.models import Course, Group, Lesson
from users.models import Subscription, CustomUser

User = get_user_model()


class LessonSerializer(serializers.ModelSerializer):
    """Список уроков."""

    course = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Lesson
        fields = (
            'title',
            'link',
            'course'
        )


class CreateLessonSerializer(serializers.ModelSerializer):
    """Создание уроков."""

    class Meta:
        model = Lesson
        fields = (
            'title',
            'link',
            'course'
        )


class StudentSerializer(serializers.ModelSerializer):
    """Студенты курса."""

    class Meta:
        model = User
        fields = (
            'first_name',
            'last_name',
            'email',
        )


class GroupSerializer(serializers.ModelSerializer):
    """Список групп."""

    # TODO Доп. задание
    students = StudentSerializer(many=True)


    class Meta:
        model = Group
        fields = (
            'title',
            'students',
            'course',
        )


class CreateGroupSerializer(serializers.ModelSerializer):
    """Создание групп."""

    class Meta:
        model = Group
        fields = (
            'title',
            'course',
            'students'
        )


class MiniLessonSerializer(serializers.ModelSerializer):
    """Список названий уроков для списка курсов."""

    class Meta:
        model = Lesson
        fields = (
            'title',
        )


class CourseSerializer(serializers.ModelSerializer):
    """Список курсов."""

    lessons = MiniLessonSerializer(many=True, read_only=True)
    lessons_count = serializers.SerializerMethodField(read_only=True)
    students_count = serializers.SerializerMethodField(read_only=True)
    groups_filled_percent = serializers.SerializerMethodField(read_only=True)
    demand_course_percent = serializers.SerializerMethodField(read_only=True)

    def get_lessons_count(self, obj):
        """Количество уроков в курсе."""
        return len(obj.lessons.all())

    def get_students_count(self, obj):
        """Общее количество студентов на курсе."""
        return len(obj.students.all())

    def get_groups_filled_percent(self, obj):
        """Процент заполнения групп, если в группе максимум 30 чел.."""
        students_count = self.get_students_count(obj)
        if students_count == 0:
            return 0
        
        groups = self.get_groups(obj)
        student_in_groups_percent = []
        for group in groups:
            student_in_groups_percent.append(len(group.students.all())/30*100)
        middle = sum(student_in_groups_percent)/10
        
        return middle
        
        # TODO

    def get_demand_course_percent(self, obj):
        """Процент приобретения курса."""
        max_students = len(CustomUser.objects.all())
        if max_students > 0:
            demand_percent = (self.get_students_count(obj) / max_students) * 100
        else:
            demand_percent = 0
        return demand_percent

    def get_lessons(self, obj):
        """Получение всех уроков курса"""
        return obj.lessons.all()
        
    def get_groups(self, obj):
        """Получение всех групп курса"""
        return Group.objects.filter(course=obj)


    class Meta:
        model = Course
        fields = (
            'id',
            'author',
            'title',
            'start_date',
            'price',
            'lessons_count',
            'lessons',
            'demand_course_percent',
            'students_count',
            'groups_filled_percent'
        )


class CreateCourseSerializer(serializers.ModelSerializer):
    """Создание курсов."""

    class Meta:
        model = Course
        fields = (
            'author',
            'title',
            'price',
            'start_date'
        )
