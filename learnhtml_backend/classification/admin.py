from django.contrib import admin
from .models import Classifier, ClassificationJob, PageDownload, ClassificationResult

admin.site.register(Classifier)
admin.site.register(ClassificationJob)
admin.site.register(PageDownload)
admin.site.register(ClassificationResult)
