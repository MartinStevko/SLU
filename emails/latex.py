from django_tex.core import compile_template_to_pdf
from django.db import models

from django.core.mail import EmailMessage, EmailMultiAlternatives
from django.template import Template
from django.conf import settings
from django.core.files.base import ContentFile
from io import BytesIO

from .models import PDFModel


class PDFModel(models.Model):
    slug = models.CharField(max_length=120)
    pdf = models.FileField(upload_to='pdfs/', null=True, blank=True)


def test():
    template = 'emails/test.tex'
    context = {'foo': 'Bar'}
    pdf = compile_template_to_pdf(template, context)
    filename = 'test.pdf'

    obj = PDFModel.objects.create(slug='test')
    obj.pdf.save(filename, ContentFile(pdf))

    email = EmailMessage(
        'Test LaTeX-u',
        'Ahoj, toto je testovacia sprava.',
        getattr(settings, 'FROM_EMAIL_NAME', 'SLU'),
        ['mstevko10@gmail.com'],
    )

    email.attach_file(obj.pdf.path)

    email.send(fail_silently=False)
