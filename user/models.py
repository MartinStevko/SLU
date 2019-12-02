from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.utils import timezone
from django.db.models.signals import post_save
from django.dispatch import receiver

from datetime import timedelta

from django.contrib.auth.models import Group
from emails.emails import SendMail


class UserManager(BaseUserManager):
    def create_user(self, email, password=None):
        if not email:
            raise ValueError('Používateľ musí mať nastavený email.')

        user = self.model(
            email=self.normalize_email(email),
            password_expiration=timezone.now()+timedelta(seconds=60)
        )

        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, email, password):
        if not email:
            raise ValueError('Používateľ musí mať nastavený email.')

        user = self.model(
            email=self.normalize_email(email),
            password_expiration=timezone.now()+timedelta(seconds=60)
        )

        user.set_password(password)

        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)

        return user


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(
        unique=True,
        help_text='E-mail na ktorý vám bude zasielaný kód na prihlásenie.'
    )

    first_name = models.CharField(
        max_length=255,
        verbose_name='meno'
    )
    last_name = models.CharField(
        max_length=255,
        verbose_name='priezvisko'
    )

    password_expiration = models.DateTimeField(
        verbose_name='expirácia kľúča',
        blank=True,
        null=True
    )

    last_login = models.DateTimeField(
        verbose_name='posledné prihlásenie',
        blank=True,
        null=True
    )

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(
        default=False,
        verbose_name='správcovský prístup'
    )
    is_central_org = models.BooleanField(
        default=False,
        verbose_name='Je centrálny organizátor'
    )

    objects = UserManager()

    USERNAME_FIELD = 'email'

    class Meta:
        verbose_name = 'používateľ'
        verbose_name_plural = 'používatelia'

        permissions = [
            ('send_creation_email', 'Can send user creation e-mail'),
        ]

    def __str__(self):
        return self.first_name + ' ' + self.last_name

    def get_full_name(self):
        return str(self)


@receiver(post_save, sender=User)
def send_user_creation_email(sender, instance, created, **kwargs):
    if created and instance.is_staff:
        SendMail(
            [instance.email],
            'Vytvorenie konta'
        ).user_creation(instance)
