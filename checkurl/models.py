from django.db import models

class URLManager(models.Model):
    url_type = models.CharField(max_length=20)
    type_explanation = models.TextField()
    malicious = models.BooleanField()



class url_judge(models.Model):
    prediction_result = models.CharField(max_length=10)
    pri_url = models.CharField(max_length=100)
    url = models.CharField(max_length=100,primary_key=True)
    ip_addr = models.CharField(max_length=50,null=True)
    nation_code = models.CharField(max_length=50,null=True)
    def __str__(self):
        return f"{self.url}"
