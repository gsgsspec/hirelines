from django.db import models

# Create your models here.

class CompanyData(models.Model):
    
    id = models.AutoField(primary_key=True)
    company_name = models.CharField(max_length=120, null=True, blank=True) 
    company_email = models.CharField(max_length=120, null=True, blank=True) 
    location = models.CharField(max_length=120, null=True, blank=True) 

    class Meta:
        db_table = 'companydata'