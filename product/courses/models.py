from django.db import models

from users.models import CustomUser

class Course(models.Model):
    """Модель продукта - курса."""

    author = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        verbose_name='Автор',
    )
    title = models.CharField(
        max_length=250,
        verbose_name='Название',
    )
    start_date = models.DateTimeField(
        auto_now=True,
        verbose_name='Дата и время начала курса'
    )

    # TODO

    price = models.IntegerField(
        verbose_name='Цена',
        default=0
    )
    lessons = models.ManyToManyField(
        'Lesson',
        related_name='courses',
        verbose_name='Уроки',
    )

    class Meta:
        verbose_name = 'Курс'
        verbose_name_plural = 'Курсы'
        ordering = ('-id',)

    def __str__(self):
        return self.title


class Lesson(models.Model):
    """Модель урока."""

    title = models.CharField(
        max_length=250,
        verbose_name='Название',
    )
    link = models.URLField(
        max_length=250,
        verbose_name='Ссылка',
    )

    # TODO

    course = models.ForeignKey(
        'Course',
        on_delete=models.CASCADE,
        verbose_name='Курс',
        null=True
    )

    class Meta:
        verbose_name = 'Урок'
        verbose_name_plural = 'Уроки'
        ordering = ('id',)

    def __str__(self):
        return self.title


class Group(models.Model):
    """Модель группы."""

    # TODO
    title = models.CharField(max_length=255, null=True)
    course = models.ForeignKey(
        'Course',
        on_delete=models.CASCADE,
        verbose_name='Курс',
        related_name='group',
        null=True
    )
    students = models.ManyToManyField(
        CustomUser,
        related_name='group',
        verbose_name='Участники',
        blank=True
    )

    class Meta:
        verbose_name = 'Группа'
        verbose_name_plural = 'Группы'
        ordering = ('-id',)

    def __str__(self):
        return self.title