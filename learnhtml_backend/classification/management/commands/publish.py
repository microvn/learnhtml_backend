import logging
import pickle

import djclick as click

from learnhtml_backend.classification.models import Classifier

# configure the logger to use the click settings
logger = logging.getLogger(__name__)


@click.command()
@click.argument('model_file', metavar='MODEL_FILE', nargs=1,
                type=click.Path(file_okay=True, dir_okay=False, readable=True))
@click.argument('name', metavar='NAME', type=str)
def command(model_file, name):
    """Upload the classifier in MODEL_FILE with NAME"""
    classifier = pickle.dumps(pickle.load(open(model_file, 'rb')))  # check proper file
    Classifier.objects.create(name=name, serialized=classifier)  # upload the object

    logger.info('Finished uploading model')
