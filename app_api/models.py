from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token

# Create your models here.

class User_data(AbstractUser):
    id = models.AutoField(primary_key=True)
    usr_email = models.CharField(max_length=120)
    usr_password = models.CharField(max_length=60)
    user = models.CharField(max_length=1,null=True) # A - Admin, S - Student

    class Meta:
        db_table = 'user_data'


@receiver(post_save, sender=User_data)
def create_auth_token_for_customer(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)


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
    status = models.CharField(max_length=1, null=True)  # P - Pending , S - Selected, R - Rejected 

    class Meta:
            db_table = 'candidate'



class JobDesc(models.Model):
    id = models.AutoField(primary_key=True)
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
    name = models.CharField(max_length=100)
    address1 = models.CharField(max_length=100, null=True, blank=True)
    address2 = models.CharField(max_length=100, null=True, blank=True)
    city = models.CharField(max_length=100, null=True, blank=True)
    state = models.CharField(max_length=100, null=True, blank=True)
    country = models.CharField(max_length=100, null=True, blank=True)
    companydomain = models.CharField(max_length=4, null=True, blank=True)
    status = models.CharField(max_length=1, null=True, blank=True) # A - Active, I - Inactive, T - Trail
    website = models.CharField(max_length=100, null=True, blank=True)
    phone1 = models.CharField(max_length=100, null=True, blank=True)
    phone2 = models.CharField(max_length=100, null=True, blank=True)
    email = models.CharField(max_length=100, null=True, blank=True)
    emaildomain = models.CharField(max_length=100,null=True)
    companytype = models.CharField(max_length=100, null=True, blank=True)
    freetrail = models.CharField(max_length=1, null=True)  # C - Completed, I - In-progress 
    registrationdate = models.DateTimeField(null=True)

    class Meta:
        db_table = 'company'


class ReferenceId(models.Model):
    type = models.CharField(max_length=1, null=True)
    prefix1 = models.CharField(max_length=3, null=True)
    prefix2 = models.CharField(max_length=3, null=True)
    prefix3 = models.CharField(max_length=3, null=True)
    lastid = models.IntegerField(null=True)

    class Meta:
        db_table = 'referenceid'


class RolesPermissions(models.Model):
    id = models.AutoField(primary_key=True)
    function = models.CharField(max_length=120, null=True)
    sub_function = models.CharField(max_length=120, null=True)
    function_category = models.CharField(max_length=120, null=True)
    function_link = models.CharField(max_length=120, null=True)
    enable = models.CharField(max_length=260, null=True)
    function_icon = models.CharField(max_length=120, null=True)
    orderby = models.IntegerField(null=True)

    class Meta:
        db_table = 'rolespermissions'


class Role(models.Model):
    id = models.AutoField(primary_key=True)
    Name = models.CharField(max_length=120, null=True)
    status = models.CharField(max_length=1, null=True)

    class Meta:
        db_table = 'role'


class User(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, null=True)
    mobile = models.CharField(max_length=20, null=True)
    location = models.CharField(max_length=120, null=True, blank=True)
    datentime = models.DateTimeField(null=True)
    email = models.CharField(max_length=120, null=True, blank=True)
    password = models.CharField(max_length=40, null=True)
    role = models.CharField(max_length=120, null=True)
    companyid = models.IntegerField(null=True)
    status = models.CharField(max_length=1, null=True) # A - Active, I - Inactive

    class Meta:
        db_table = 'user'