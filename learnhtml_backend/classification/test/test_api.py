import pickle
from datetime import datetime

import learnhtml
from rest_framework.test import APITestCase

from learnhtml_backend.classification.models import PageDownload, Classifier, ClassificationJob


class TestClassificationSerializers(APITestCase):
    def setUp(self):
        """Create a working hierarchy of objects"""
        self.pages = [
            PageDownload.objects.create(url='https://google.com',
                                        content='<html><body></body></html>'),
            PageDownload.objects.create(url='https://google2.com',
                                        content='<html><body>2</body></html>'),
        ]

        # add a classifier
        classifier, _ = learnhtml.model_selection.get_param_grid(heihgt=2, depth=3,
                                                                 classify='tree', use_numeric=True)
        self.classifiers = [
            Classifier.objects.create(name='some classifier',
                                      serialized=pickle.dumps(classifier))
        ]

        # create 1 successful, 1 failed an one pending
        self.jobs = [
            ClassificationJob.objects.create(classified_page=self.pages[0],
                                             classifier_used=self.classifiers[0],
                                             date_ended=datetime.now(), is_failed=False),
            ClassificationJob.objects.create(classified_page=self.pages[0],
                                             classifier_used=self.classifiers[0],
                                             date_ended=datetime.now(), is_failed=True),
            ClassificationJob.objects.create(classified_page=self.pages[1],
                                             classifier_used=self.classifiers[0])
        ]

    def test_page_serializers(self):
        """Test detail and list serializer for pages"""
        expected_data = 0
        pass
