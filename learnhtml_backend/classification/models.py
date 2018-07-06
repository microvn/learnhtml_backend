from datetime import datetime

from django.core import validators
from django.db import models


class PageDownload(models.Model):
    """Page Download"""
    url = models.TextField(help_text='Url',
                           validators=[validators.URLValidator()],
                           null=False, unique=True)
    content = models.TextField(help_text='Html content(if null it means it hasn\'t been downloaded yet',
                               blank=False, null=True)
    date_downloaded = models.DateTimeField(help_text='Date created', auto_now=True, null=True)

    class Meta:
        ordering = ('-id',)


class Classifier(models.Model):
    """Persisted classifier"""
    name = models.CharField(help_text='Name', max_length=255, blank=False, null=False)
    date_trained = models.DateTimeField(help_text='Date trained', auto_now_add=True, null=False)
    serialized = models.BinaryField(help_text='Pickle')

    class Meta:
        ordering = ('-id',)


class ClassificationJob(models.Model):
    """Classification task"""
    classified_page = models.ForeignKey(to=PageDownload, help_text='The classified page instance', related_name='jobs',
                                        on_delete=models.CASCADE)
    classifier_used = models.ForeignKey(to=Classifier, help_text='Which classifier was used', related_name='jobs',
                                        on_delete=models.CASCADE)
    date_started = models.DateTimeField(help_text='Date when job was created', auto_now_add=True, null=False)
    date_ended = models.DateTimeField(help_text='Date when the job ended', null=True, default=None)
    is_failed = models.BooleanField(help_text='Whether the job failed or not', default=False)

    @property
    def is_finished(self):
        """Whether the job finished"""
        return self.date_ended is None

    def set_finished(self):
        """Set the job as finished in this moment"""
        self.date_ended = datetime.now()
        self.is_failed = False

    def set_failed(self):
        """Set ghe job as finished in this moment"""
        self.date_ended = datetime.now()
        self.is_failed = True

    class Meta:
        ordering = ('-id',)


class ClassificationResult(models.Model):
    """Path and classification job. If present it means that the
    xpath denotes a positive class."""
    xpath = models.TextField(help_text='The xpath which contains a positive label')
    job = models.ForeignKey(to=ClassificationJob, help_text='The classification job this result corresponds to',
                            related_name='results', on_delete=models.CASCADE)

    class Meta:
        ordering = ('-id',)
