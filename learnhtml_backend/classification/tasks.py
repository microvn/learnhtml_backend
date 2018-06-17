"""Async worker task definition"""
import logging
import pickle

import webpage2html
from django.db import transaction
from django.utils import timezone
from django_rq import job
from learnhtml.extractor import HTMLExtractor

from learnhtml_backend.classification.models import ClassificationJob, ClassificationResult

logger = logging.getLogger(__name__)


@job
def do_classification_job(classification_job_id):
    """Given a classification job object, download the
    page in the background and classify the content."""
    classification_job = ClassificationJob.objects.get(id=classification_job_id)
    url = classification_job.classified_page.url
    html_content = classification_job.classified_page.content  # load he content, may be None
    classifier = pickle.loads(classification_job.classifier_used.serialized)  # load classifier

    try:
        if html_content is None:
            # download page first if not in DB
            logger.info('Downloading webpage')
            html_content = webpage2html.generate(url)

            # update the downloaded content
            # we at least want to keep the HTML
            with transaction.atomic():
                # save the content
                logger.info('Webpage downloaded')
                classification_job.classified_page.content = html_content
                classification_job.classified_page.save()
        else:
            logger.info('Webpage in DB. Skipping download')

        # try to classify the html content
        extractor = HTMLExtractor(classifier)  # get the extractor
        paths = extractor.extract_from_html(html_content)

        # create a list to bulk create later
        result_list = [ClassificationResult(job=classification_job, xpath=path) for path in paths]

        with transaction.atomic():
            # save the classification result
            ClassificationResult.objects.bulk_create(result_list)

            # and specify success if it reaches this point
            # we want to either set it all as a success or none
            classification_job.is_failed = False
            classification_job.date_ended = timezone.now()
            classification_job.save()
    except Exception as exce:
        # end the job as a failure
        classification_job.is_failed = True
        classification_job.date_ended = timezone.now()
        classification_job.save()
