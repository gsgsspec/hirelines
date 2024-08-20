from django.db import models

# Create your models here.

class CompanyData(models.Model):
    
    id = models.AutoField(primary_key=True)
    companyname = models.CharField(max_length=120, null=True, blank=True) 
    companyemail = models.CharField(max_length=120, null=True, blank=True) 
    location = models.CharField(max_length=120, null=True, blank=True) 
    contactperson = models.CharField(max_length=50, null=True, blank=True) 
    companytype = models.CharField(max_length=100, null=True, blank=True)
    registerationtime = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'companydata'



class Candidate(models.Model):
    id = models.AutoField(primary_key=True) 
    candidateid = models.CharField(max_length=100,null=True)
    firstname = models.CharField(max_length=100, null=True)
    lastname = models.CharField(max_length=100, null=True)
    registrationdate = models.DateTimeField(null=True)
    companyid = models.IntegerField(null=True)
    paperid = models.IntegerField(null=True, blank=True)
    email = models.CharField(max_length=100, null=True)
    mobile = models.CharField(max_length=40, null=True)
    add1 = models.CharField(max_length=100, null=True)
    add2 = models.CharField(max_length=100, null=True)
    city = models.CharField(max_length=100, null=True)
    state = models.CharField(max_length=100, null=True)
    country = models.CharField(max_length=40, null=True)
    dob = models.DateField(null=True)
    jobid = models.IntegerField(null=True)
    status = models.CharField(max_length=1, null=True)

    class Meta:
            db_table = 'candidate'



class JobDesc(models.Model):
    id = models.AutoField(primary_key=True)
    jobcode = models.CharField(max_length=10, null=True)
    title = models.CharField(max_length=100, null=True)
    description = models.CharField(max_length=1024, null=True)
    expmin = models.IntegerField(null=True)
    expmax = models.IntegerField(null=True)
    role = models.CharField(max_length=100,null=True)
    department = models.CharField(max_length=100,null=True)
    location = models.CharField(max_length=512, null=True)
    budget = models.DecimalField(max_digits=13, decimal_places=2, null=True)
    skillset = models.CharField(max_length=512, null=True)
    skillnotes = models.CharField(max_length=512, null=True)
    interviewers = models.CharField(max_length=51,null=True)
    expjoindate = models.DateField(max_length=11,null=True)
    positions = models.IntegerField(null=True)
    createdby = models.IntegerField(null=True)
    status = models.CharField(max_length=1, null=True) # O - Open, C - Closed

    class Meta:
        db_table = 'jobdesc'


class Registration(models.Model):
     
    id = models.AutoField(primary_key=True)
    candidateid = models.IntegerField(null=True)
    jobid = models.IntegerField(null=True)
    paperid = models.IntegerField(null=True)
    papertype = models.CharField(max_length=1, null=True, blank=True)
    companyid = models.IntegerField(null=True)
    registrationdate = models.DateTimeField(null=True)
    status = models.CharField(max_length=1, null=True, blank=True) 

    class Meta:
        db_table = 'registration'


class Company(models.Model):
    id = models.AutoField(primary_key=True)
    company_name = models.CharField(max_length=100)
    company_add1 = models.CharField(max_length=100, null=True, blank=True)
    company_add2 = models.CharField(max_length=100, null=True, blank=True)
    company_city = models.CharField(max_length=100, null=True, blank=True)
    company_state = models.CharField(max_length=100, null=True, blank=True)
    company_country = models.CharField(max_length=100, null=True, blank=True)
    company_domain = models.CharField(max_length=4, null=True, blank=True)
    company_status = models.CharField(max_length=1, null=True, blank=True)
    company_organization = models.IntegerField(null=True)
    company_website = models.CharField(max_length=100, null=True, blank=True)
    company_phone1 = models.CharField(max_length=100, null=True, blank=True)
    company_phone2 = models.CharField(max_length=100, null=True, blank=True)
    company_email = models.CharField(max_length=100, null=True, blank=True)

    class Meta:
        db_table = 'company'

