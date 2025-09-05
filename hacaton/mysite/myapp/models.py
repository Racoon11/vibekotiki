from django.db import models
from django.utils import timezone

class Article(models.Model):
    title = models.CharField(max_length=200, verbose_name="Заголовок")
    content = models.TextField(verbose_name="Содержание")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Статья"
        verbose_name_plural = "Статьи"
 

class User(models.Model):
    tg = models.IntegerField(verbose_name="Telegram ID")  # Поле для хранения Chat Id
    UserName = models.CharField(max_length=200, default='unknown')
    Name = models.CharField(max_length=255, verbose_name="Имя")  # Текстовое поле (аналог TEXT)
    DayAdviceSubscriber = models.BooleanField(default=False)
    EventsSubscriber = models.BooleanField(default=False)

class UserInfo(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_info', verbose_name="Пользователь")
    disorder = models.CharField("Нарушение", max_length=255)
    date = models.DateTimeField("Дата и время", default=timezone.now)

class Question(models.Model):
    from_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='questions')
    text = models.TextField()
    solved = models.BooleanField(default=False)
    answer = models.TextField(default='')

class Event(models.Model):
    name = models.CharField(max_length=200, verbose_name="Название мероприятия")
    organizer = models.CharField(max_length=100, verbose_name="Организатор")
    description = models.TextField(verbose_name="Описание мероприятия", blank=True)
    event_date = models.DateField(verbose_name="Дата проведения")
    start_time = models.TimeField(verbose_name="Время начала")
    location = models.CharField(max_length=200, verbose_name="Место проведения")
    max_participants = models.PositiveIntegerField(
        verbose_name="Максимальное количество участников",
        default=20
    )
    created_at = models.DateTimeField(auto_now_add=True)