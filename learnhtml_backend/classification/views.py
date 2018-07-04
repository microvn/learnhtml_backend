from django.db.models import Q, ExpressionWrapper, F, DurationField
from django.utils import timezone
from rest_framework import viewsets, mixins
from rest_framework.decorators import action

from learnhtml_backend.classification.models import PageDownload, Classifier, ClassificationJob
from learnhtml_backend.classification.serializers import PageListSerializer, PageDetailSerializer, ClassifierSerializer, \
    JobDetailSerializer, JobListSerializer
from learnhtml_backend.consts import CLASSIFY_TIMEOUT


class PageViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for downloaded pages. Ony the detail view exposes
    the html content."""
    queryset = PageDownload.objects.all()

    def get_serializer_class(self):
        """Conditional serializer based on action"""
        if self.action == 'list':
            return PageListSerializer
        if self.action == 'retrieve':
            return PageDetailSerializer
        return PageListSerializer


class ClassifierViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for classifiers, just for viewing."""
    queryset = Classifier.objects.all()
    serializer_class = ClassifierSerializer


class JobViewSet(mixins.ListModelMixin,
                 mixins.RetrieveModelMixin,
                 mixins.CreateModelMixin,
                 viewsets.GenericViewSet):
    """ViewSet for Classification jobs and their results.
    Allows viewing an overview of all, completed, failed and pending jobs.
    Detail view returns the classified page and the corresponding labels.

    New jobs can be posted to this endpoint as well.
    """
    queryset = Classifier.objects.all()

    def get_serializer_class(self):
        """Conditional serializer class"""
        if self.action == 'retrieve':
            return JobDetailSerializer
        return JobListSerializer

    def get_queryset(self):
        # return in the descending order
        queryset = ClassificationJob.objects.all().order_by('-date_started')

        # conditional filtering based on the action
        if self.action == 'failed':
            # show only the failed ones
            queryset = queryset.annotate(elapsed_time=ExpressionWrapper(timezone.now() - F('date_started'),
                                                                        output_field=DurationField()))
            queryset = queryset.filter(Q(is_failed=True) | Q(date_ended__isnull=True,
                                                             elapsed_time__gt=CLASSIFY_TIMEOUT))
        if self.action == 'pending':
            # show only the pending ones
            queryset = queryset.annotate(elapsed_time=ExpressionWrapper(timezone.now() - F('date_started'),
                                                                        output_field=DurationField()))
            queryset = queryset.filter(is_failed=False, date_ended__isnull=True, elapsed_time__lte=CLASSIFY_TIMEOUT)
        if self.action == 'done':
            # just the finished ones
            queryset = queryset.filter(is_failed=False, date_ended__isnull=False)

        return queryset

    @action(detail=False)
    def failed(self, request, *args, **kwargs):
        # pass it down to list, get_queryset takes
        # care of the rest
        return self.list(request, *args, **kwargs)

    @action(detail=False)
    def pending(self, request, *args, **kwargs):
        # the same as failed
        return self.list(request, *args, **kwargs)

    @action(detail=False)
    def done(self, request, *args, **kwargs):
        # again
        return self.list(request, *args, **kwargs)
