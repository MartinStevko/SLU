from django.db import models
from django.utils import timezone
from django.core.validators import RegexValidator

from datetime import datetime

CATEGORIES = (
    ('rules', 'Pravidlá'),
    ('ultimate', 'O ultimate'),
    ('other', 'Iné'),
)


class News(models.Model):
    title = models.CharField(max_length=127)
    expiration = models.DateTimeField()

    description = models.TextField()
    image = models.ImageField(upload_to='news')

    class Meta:
        verbose_name_plural = 'news'

    def expired(self):
        if self.expiration.replace(tzinfo=None) > datetime.now():
            return False
        else:
            return True

    def __str__(self):
        return '{}'.format(self.title)


class Section(models.Model):
    title = models.CharField(max_length=127)
    category = models.CharField(
        max_length=15,
        default='other',
        choices=CATEGORIES
    )

    description = models.TextField()
    image = models.ImageField(upload_to='sections')

    def __str__(self):
        return '{}'.format(self.title)


class Message(models.Model):
    from_email = models.EmailField()
    send_time = models.DateTimeField(default=timezone.now)

    subject = models.CharField(max_length=255, blank=True, null=True)
    text = models.TextField()

    def __str__(self):
        return '{} - {}'.format(self.subject, self.text)


class OrganizerProfile(models.Model):
    full_name = models.CharField(max_length=255)
    email = models.EmailField()
    image = models.ImageField(upload_to='organizers')

    start_season = models.CharField(
        max_length=15,
        validators=[
            RegexValidator(
                regex='^((leto|zima), \d{4}|-)$',
                message='Začiatok aj koniec sezóny musia byť vo formáte leto/zima, YYYY.',
            ),
        ]
    )
    end_season = models.CharField(
        max_length=15,
        default='-',
        validators=[
            RegexValidator(
                regex='^((leto|zima), \d{4}|-)$',
                message='Začiatok aj koniec sezóny musia byť vo formáte leto/zima, YYYY.',
            ),
        ]
    )

    def __str__(self):
        return '{}'.format(self.full_name)
