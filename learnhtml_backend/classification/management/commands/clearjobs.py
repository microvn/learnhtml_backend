import django_rq
import djclick as click

from learnhtml_backend.classification import tasks


@click.command()
def command():
    """Clear the database of expired jobs"""
    django_rq.enqueue(tasks.do_clear_jobs)
    click.echo('Enqueued cleaning job')
