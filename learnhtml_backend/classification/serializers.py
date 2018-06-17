import pickle

import django_rq
from rest_framework import serializers

from learnhtml_backend.classification import tasks
from learnhtml_backend.classification.models import ClassificationJob, PageDownload, Classifier


class PageDetailSerializer(serializers.ModelSerializer):
    """Serializer used for the detail view of a page.
    Can be used to download content"""

    class Meta:
        model = PageDownload
        fields = ('id', 'url', 'content', 'date_downloaded')


class PageListSerializer(serializers.ModelSerializer):
    """List serializer for pages. Does not include content"""
    is_failed = serializers.SerializerMethodField()

    def get_is_failed(self, obj):
        return obj.content is None

    class Meta:
        model = PageDownload
        fields = ('id', 'url', 'is_failed', 'date_downloaded')


class JobListSerializer(serializers.ModelSerializer):
    """Job serializer for lists. Does not include large info."""
    url = serializers.URLField(source='classified_page.url')
    classifier_used = serializers.PrimaryKeyRelatedField(many=False, queryset=Classifier.objects.all())

    def create(self, validated_data):
        """Custom create"""
        url = validated_data.pop('classified_page').pop('url')
        classifier_used = validated_data.pop('classifier_used')
        # if url is in database use the existing pagedownloaded
        page = PageDownload.objects.filter(url=url).first()

        if page is not None and page.content is None:
            # this means it hans't been downloaded
            # do the same as if it were None
            page.delete()
            page = None

        if page is None:
            # queue another download
            page = PageDownload.objects.create(url=url, content=None)

        # create classification job with this
        job = ClassificationJob.objects.create(classifier_used=classifier_used,
                                               classified_page=page)
        django_rq.enqueue(tasks.do_classification_job, job.id)

        # return the job
        return job

    class Meta:
        model = ClassificationJob
        fields = ('id', 'classifier_used', 'url', 'is_failed', 'date_started', 'date_ended')
        read_only_fields = ('id', 'is_failed', 'date_started', 'date_ended')


class JobDetailSerializer(serializers.ModelSerializer):
    """Job serializer for details. Includes HTML results"""
    url = serializers.URLField(source='classified_page.url')
    page_id = serializers.PrimaryKeyRelatedField(source='classified_page', read_only=True)
    results = serializers.SerializerMethodField()

    def get_results(self, obj):
        return obj.results.values_list('xpath', flat=True)

    class Meta:
        model = ClassificationJob
        fields = ('id', 'url', 'page_id', 'results', 'is_failed',
                  'date_started', 'date_ended')


class ClassifierSerializer(serializers.ModelSerializer):
    """Serializer for classifiers"""
    params = serializers.SerializerMethodField()

    def get_params(self, obj):
        """Return a representation of the params"""
        return {param: str(val) for param, val in
                pickle.loads(obj.serialized).get_params(deep=True).items()}

    class Meta:
        model = Classifier
        fields = ('id', 'name', 'date_trained', 'params')
