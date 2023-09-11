from django.db import models

class URLManager(models.Model):
    url_type = models.CharField(max_length=20)
    type_explanation = models.TextField()
    malicious = models.BooleanField()