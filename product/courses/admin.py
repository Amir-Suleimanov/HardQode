from django.contrib import admin

from courses.models import Group, Lesson, Course
# Register your models here.

@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ('title', 'link',)


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'price')
    filter_horizontal = ('lessons',)


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ('course', )
    filter_horizontal = ('students',)