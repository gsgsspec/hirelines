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
    # paperid = models.IntegerField(null=True, blank=True)
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
    jdlibraryid = models.IntegerField(null=True)
    title = models.CharField(max_length=350, null=True)
    role = models.CharField(max_length=100,null=True)
    description = models.CharField(max_length=3024, null=True)
    expmin = models.IntegerField(null=True)
    expmax = models.IntegerField(null=True)
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
    companyid = models.IntegerField(null=True)

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
    companydomain = models.CharField(max_length=100, null=True, blank=True)
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


class Workflow(models.Model):
    id = models.AutoField(primary_key=True)
    jobid = models.IntegerField(null=True)
    companyid = models.IntegerField(null=True)
    paperid = models.IntegerField(null=True)
    papertype = models.CharField(max_length=1, null=True)
    order = models.IntegerField(null=True)
    papertitle = models.CharField(max_length=120, null=True, blank=True)

    class Meta:
        db_table = 'workflow'


class CallSchedule(models.Model):
    id = models.AutoField(primary_key=True)
    candidateid = models.IntegerField(null=True)
    hrid = models.IntegerField(null=True)
    paper_id = models.IntegerField(null=True)
    interviewerid = models.IntegerField(null=True)
    datentime = models.DateTimeField(null=True)
    status = models.CharField(max_length=1, null=True)
    callstarteddtt = models.DateTimeField(null=True)
    callendeddtt = models.DateTimeField(null=True)
    intnotes = models.CharField(max_length=1000, null=True)
    meetinglink = models.CharField(max_length=100, null=True)
    callendflag = models.CharField(max_length=1,null=True)
    companyid = models.IntegerField(null=True)

    class Meta:
        db_table = 'callschedule'


class Vacation(models.Model):
    id = models.AutoField(primary_key=True)
    empid = models.IntegerField(null=True)
    fromdate = models.DateField(null=True)
    todate = models.DateField(null=True)
    hours = models.IntegerField(null=True)
    purpose = models.CharField(max_length=30, null=True)
    type = models.CharField(max_length=1, null=True)
    companyid = models.IntegerField(null=True)

    class Meta:
        db_table = 'vacation'


class WorkCal(models.Model):
    id = models.AutoField(primary_key=True)
    empid = models.IntegerField(null=True)
    startday = models.CharField(max_length=3, null=True)
    starttime = models.TimeField(max_length=20, null=True)
    workhours = models.CharField(max_length=4,null=True)
    weekoff1 = models.CharField(max_length=3, null=True)
    weekoff2 = models.CharField(max_length=3, null=True)
    companyid = models.IntegerField(null=True)

    class Meta:
        db_table = 'workcal'


class ExtendedHours(models.Model):
    id = models.AutoField(primary_key=True)
    empid = models.IntegerField(null=True)
    workcalid = models.IntegerField(null=True)
    fromdate = models.DateField(null=True)
    todate = models.DateField(null=True)
    starttime = models.TimeField(max_length=20, null=True)
    workhours = models.CharField(max_length=4,null=True)
    status = models.CharField(max_length=1, null=True) # A - Active, I - Inactive/Removed 
    companyid = models.IntegerField(null=True)

    class Meta:
        db_table = 'extendedhours'


class HolidayCal(models.Model):
    id = models.AutoField(primary_key=True)
    holidaydt = models.DateField(null=True)
    type = models.CharField(max_length=1, null=True)
    description = models.CharField(max_length=100, null=True)
    companyid = models.IntegerField(null=True)

    class Meta:
        db_table = 'holidaycal'


class Email_template(models.Model):
    id = models.AutoField(primary_key=True)
    company_id = models.IntegerField(null=True, blank=True)
    template_name = models.CharField(max_length=120, null=True)
    paper_type =  models.CharField(max_length=100, null=True)
    event = models.CharField(max_length=120, null=True)
    sender_email = models.CharField(max_length=100, null=True)
    sender_label = models.CharField(max_length=100, null=True)
    email_subject = models.CharField(max_length=300, null=True, blank=True)
    email_body = models.CharField(max_length=10000, null=True, blank=True)
    template_heading = models.CharField(max_length=300, null=True)
    # email_attachment = models.CharField(max_length=250, null=True)
    # email_attachment_path = models.FileField(upload_to="email_attachments/", null=True)
    # email_attachment_name = models.CharField(max_length=120, null=True)

    
    class Meta:
        db_table = 'email_template'


class Branding(models.Model):
    id = models.AutoField(primary_key=True)
    companyid = models.IntegerField(null=True)
    logourl = models.FileField(upload_to="logos/", null=True)
    content = models.TextField(null=True)
    sociallinks = models.TextField(null=True)
    status = models.CharField(max_length=1, null=True)

    class Meta:
        db_table = 'branding'


class Lookupmaster(models.Model):
    id = models.AutoField(primary_key=True)
    lookupid = models.IntegerField(null=True)
    lookupmasterid = models.IntegerField(null=True)
    lookupname = models.CharField(max_length=150, null=True)
    lookupparam1 = models.TextField(null=True)
    lookupparam2 = models.CharField(max_length=150, null=True)
    status = models.CharField(max_length=1, null=True)
    comments = models.CharField(max_length=300, null=True)

    class Meta:
        db_table = 'lookupmaster'


class QResponse(models.Model):
    id = models.AutoField(primary_key=True)
    qid = models.IntegerField(null=True)
    candidateid = models.IntegerField(null=True)
    callscheduleid = models.IntegerField(null=True)
    response = models.CharField(max_length=256,null=True)
    notes = models.CharField(max_length=256,null=True)
    qrate = models.CharField(max_length=10,null=True)
    companyid = models.IntegerField(null=True)

    class Meta:
        db_table = 'qresponse'


class CdnData(models.Model):
    id = models.AutoField(primary_key=True)
    libraryid = models.CharField(max_length=50, null=True)
    libraryname = models.CharField(max_length=100, null=True)
    pullzoneid = models.CharField(max_length=100,null=True)
    hostname = models.CharField(max_length=100,null=True)
    authkey = models.CharField(max_length=100,null=True)

    class Meta:
        db_table = 'cdndata'


class InterviewMedia(models.Model):
    id = models.AutoField(primary_key=True)
    recorded = models.CharField(max_length=200, null=True)
    candidateid = models.CharField(max_length=40, null=True)
    scheduleid = models.IntegerField(null=True)

    class Meta:
        db_table = 'interviewmedia'


class IvFeedback(models.Model):
    candidateid = models.IntegerField(null=True)
    gonogo = models.CharField(max_length=1, null=True)
    interviewerid = models.IntegerField(null=True)
    notes = models.CharField(max_length=100,null=True)
    companyid = models.IntegerField(null=True)
    
    class Meta:
        db_table = 'ivfeedback'
