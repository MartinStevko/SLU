from django.db import models
from django.utils import timezone

CATEGORIES = [
    ('rules', 'Pravidlá'),
    ('ultimate', 'O ultimate'),
    ('other', 'Iné'),
]


class Section(models.Model):
    title = models.CharField(max_length=100)
    category = models.CharField(max_length=10, default='other', choices=CATEGORIES)

    description = models.TextField()
    image = models.ImageField(upload_to='sections')

    def __str__(self):
        return '{}'.format(self.title)


class News(models.Model):
    title = models.CharField(max_length=100)
    expiration = models.DateTimeField()

    description = models.TextField()
    image = models.ImageField(upload_to='news')

    class Meta:
        verbose_name_plural = 'news'

    def __str__(self):
        return '{}'.format(self.title)


class Message(models.Model):
    from_email = models.EmailField()
    send_time = models.DateTimeField(default=timezone.now)

    subject = models.CharField(max_length=200, blank=True, null=True)
    text = models.TextField()

    def __str__(self):
        return '{} - {}'.format(self.subject, self.text)


class Organizer(models.Model):
    full_name = models.CharField(max_length=200)
    email = models.EmailField()
    image = models.ImageField(upload_to='organizers')

    start_season = models.CharField(max_length=20)
    end_season = models.CharField(max_length=20, default='-')

    def __str__(self):
        return '{}'.format(self.full_name)
