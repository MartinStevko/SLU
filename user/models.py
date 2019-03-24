from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

from app.emails import SendMail


class SpecialPermission(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        verbose_name='používateľ',
    )

    email_verified = models.BooleanField(
        default=False,
        verbose_name='potvrdený e-mail',
    )

    def __str__(self):
        return "{}".format(self.user.get_full_name())

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        SpecialPermission.objects.create(user=instance)

        SendMail(
            [instance.email],
            'Potvrdenie e-mailovej adresy'
        ).user_creation(instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.specialpermission.save()
