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
    demorequest = models.CharField(max_length=1, null=True, blank=True) 

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
    deleteflag = models.CharField(max_length=1, null=True) # Y - Marked as deleted
    source = models.CharField(max_length=5,null=True)
    profileid = models.IntegerField(null=True)

    class Meta:
            db_table = 'candidate'


class JobDesc(models.Model):
    id = models.AutoField(primary_key=True)
    jobcode = models.CharField(max_length=20,null=True)
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
    secondaryskills = models.CharField(max_length=2048, null=True)
    skillnotes = models.CharField(max_length=512, null=True)
    interviewers = models.CharField(max_length=100,null=True)
    expjoindate = models.DateField(max_length=11,null=True)
    positions = models.IntegerField(null=True)
    createdby = models.IntegerField(null=True)
    createdon = models.DateTimeField(null=True)
    companyid = models.IntegerField(null=True)
    status = models.CharField(max_length=1, null=True) # D - Draft, P - Publish , S - Stopped , I - Close 
    dashboardflag = models.CharField(max_length=1, null=True)
    approval_status = models.CharField(max_length=1, null=True)
    comments = models.CharField(max_length=100, null=True)
    recruiterids = models.CharField(max_length=100,null=True)
    hiringmanagerid= models.IntegerField(null=True)

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
    completiondate = models.DateTimeField(null=True)
    status = models.CharField(max_length=1, null=True, blank=True) # (For Interview : O - Offered, H - Hold)

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
    contactperson = models.CharField(max_length=100, null=True, blank=True)
    resumetemplateid = models.IntegerField(null=True)

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
    paperlibraryid = models.IntegerField(null=True)
    teststatus = models.CharField(max_length=1, null=True) # A - Active, I - Inactive

    class Meta:
        db_table = 'workflow'


class Brules(models.Model):
    id = models.AutoField(primary_key=True)
    workflowid = models.IntegerField(null=True, blank=True)
    companyid = models.IntegerField(null=True, blank=True)
    jobdescid  = models.IntegerField(null=True, blank=True)
    paperid = models.IntegerField(null=True, blank=True)
    passscore = models.IntegerField(null=True, blank=True)
    passevent = models.IntegerField(null=True, blank=True) # email template id
    failevent = models.IntegerField(null=True, blank=True) # email template id
    hold = models.CharField(max_length=1,null=True,blank=True) # hold candidate "Y"  Or "N"
    holdpercentage = models.IntegerField(null=True, blank=True) # hold candidate percentage

    class Meta:
        db_table = 'brules'


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
    instructions = models.CharField(max_length=1000, null=True)
    intnotes = models.CharField(max_length=1000, null=True)
    meetinglink = models.CharField(max_length=100, null=True)
    callendflag = models.CharField(max_length=1,null=True)
    companyid = models.IntegerField(null=True)
    audioscore = models.IntegerField(null=True)
    audiolevel = models.CharField(max_length=1,null=True) # H - High, M - Moderate, L - Low

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
    userid = models.IntegerField(null=True)
    startday = models.CharField(max_length=10, null=True)
    starttime = models.TimeField(max_length=20, null=True)
    hours = models.CharField(max_length=4,null=True)
    weekoff1 = models.CharField(max_length=10, null=True)
    weekoff2 = models.CharField(max_length=10, null=True)
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
    email_attachment = models.CharField(max_length=250, null=True)
    email_attachment_path = models.FileField(upload_to="email_attachments/", null=True)
    email_attachment_name = models.CharField(max_length=120, null=True)

    
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


# holds one record per registered company
class Account(models.Model):
    id = models.AutoField(primary_key=True)
    companyid = models.IntegerField(null=True)
    type = models.CharField(max_length=1, null=True)
    payment = models.DecimalField(max_digits=13, decimal_places=2, null=True) # total amount paid
    credit = models.IntegerField(null=True) # total added credits
    lastpayment = models.DecimalField(max_digits=13, decimal_places=2, null=True)
    lastpaymentdatetime = models.DateTimeField(null=True)
    lastcredit = models.IntegerField(null=True) # last added credits
    lastcreditdatetime = models.DateTimeField(null=True)
    balance = models.IntegerField(null=True) # balance credits
    lowcreditsnotification = models.CharField(max_length=1, null=True,blank=True)

    class Meta:
        db_table = 'account'


# holds mutiple records ie. each payment
class Payments(models.Model):
    id = models.AutoField(primary_key=True)
    companyid = models.IntegerField(null=True)
    dateofpay = models.DateTimeField(null=True)
    modeofpay = models.CharField(max_length=1, null=True)
    amount = models.DecimalField(max_digits=13, decimal_places=2, null=True)
    credits = models.IntegerField(null=True)

    class Meta:
        db_table = 'payments'


# holds mutiple records ie. each transaction
class Credits(models.Model):
    id = models.AutoField(primary_key=True)
    companyid = models.IntegerField(null=True)
    transdatetime = models.DateTimeField(null=True)
    transtype = models.CharField(max_length=1, null=True) # Credit / Debit
    papertype = models.CharField(max_length=1, null=True) # papertype
    points = models.IntegerField(null=True) # credits used
    user = models.IntegerField(null=True) # hrid / interviewer
    transid = models.IntegerField(null=True) # paperid/regid
    balance = models.IntegerField(null=True)

    class Meta:
        db_table = 'credits'


# holds mutiple records ie. each company each type
class CompanyCredits(models.Model):
    id = models.AutoField(primary_key=True)
    companyid = models.IntegerField(null=True)
    transtype = models.CharField(max_length=1, null=True) # papertype
    credits = models.IntegerField(null=True) # credits charged

    class Meta:
        db_table = 'companycredits'


class JdAnalysis(models.Model):
    id = models.AutoField(primary_key=True)
    companyid = models.IntegerField(null=True)
    sourcecode = models.CharField(max_length=5,null=True)
    papertype = models.CharField(max_length=1, null=True)
    registration = models.IntegerField(null=True)
    submission = models.IntegerField(null=True)
    efficiency = models.IntegerField(null=True)
    durationmin = models.IntegerField(null=True) # in minutes
    durationmax = models.IntegerField(null=True) # in minutes
    durationavg = models.IntegerField(null=True) # in minutes
    jobid = models.IntegerField(null=True)
    leadtimemin = models.IntegerField(null=True) # in minutes
    leadtimemax = models.IntegerField(null=True) # in minutes
    leadtimeavg = models.IntegerField(null=True) # in minutes

    class Meta:
        db_table = 'jdanalysis'


class Source(models.Model):
    id = models.AutoField(primary_key=True)
    code = models.CharField(max_length=5, null=True)
    label = models.CharField(max_length=50, null=True)
    userid = models.IntegerField(null=True)
    companyid = models.IntegerField(null=True)

    class Meta:
        db_table = 'source'


class Uploads(models.Model):
    id = models.AutoField(primary_key=True)
    companyid = models.IntegerField(null=True)
    type = models.CharField(max_length=1,null=True) # C - Candidate upload
    filepath = models.CharField(max_length=200, null=True)
    filename = models.CharField(max_length=100, null=True)
    status = models.CharField(max_length=1,null=True)

    class Meta:
        db_table = 'uploads'



class Resume(models.Model):
    id = models.AutoField(primary_key=True)
    sourceid = models.IntegerField(null=True)
    filename =  models.CharField(max_length=100, null=True)
    mailid =  models.CharField(max_length=200, null=True)
    datentime = models.DateTimeField(auto_now_add=True)
    companyid = models.IntegerField(null=True)
    status = models.CharField(max_length=1,null=True) # P - Pending Review, D - Soft Deleted, A - Added to Profile
    docparserid = models.IntegerField(null=True)
    jobid = models.IntegerField(null=True)

    class Meta:
        db_table = "resume"


class ResumeFile(models.Model):
    id = models.AutoField(primary_key=True)
    resumeid = models.IntegerField(null=True)
    filename =  models.CharField(max_length=100, null=True)
    filecontent = models.BinaryField(null=True)

    class Meta:
        db_table = "resumefile"


class Profile(models.Model):
    id = models.AutoField(primary_key=True)
    sourceid = models.IntegerField(null=True, blank=True)
    resumeid = models.IntegerField(null=True, blank=True)
    companyid = models.IntegerField(null=True)
    dateofcreation = models.DateTimeField(null=True, blank=True)
    title = models.CharField(max_length=100, null=True, blank=True)
    firstname = models.CharField(max_length=100, null=True, blank=True)
    middlename = models.CharField(max_length=40, null=True, blank=True)
    lastname = models.CharField(max_length=100, null=   True, blank=True)
    email = models.CharField(max_length=100, null=True, blank=True)
    mobile = models.CharField(max_length=50, null=True, blank=True)
    linkedin = models.CharField(max_length=100, null=True, blank=True)
    facebook = models.CharField(max_length=100, null=True, blank=True)
    passportnum = models.CharField(max_length=40, null=True, blank=True)
    dateofbirth = models.DateTimeField(null=True, blank=True)
    fathername = models.CharField(max_length=100, null=True, blank=True)
    nativeof = models.CharField(max_length=100, null=True, blank=True)
    strength = models.IntegerField(null=True)
    educationscore = models.IntegerField(null=True)
    experiencescore = models.IntegerField(null=True)
    projectsscore = models.IntegerField(null=True)
    skillsscore = models.IntegerField(null=True)
    certificatesscore = models.IntegerField(null=True)
    awardsscore = models.IntegerField(null=True)
    status = models.CharField(max_length=1, null=True, blank=True) #  D - Draft, R - Rejected, O - Offered, E - Employee
    profilecode=models.CharField(null=True,blank=True,max_length=20)

    class Meta:
        db_table = 'profile'


class ProfileEducation(models.Model):
    id = models.AutoField(primary_key=True)
    profileid = models.IntegerField(null=True, blank=True)
    sequence = models.IntegerField(null=True, blank=True)
    course = models.CharField(max_length=100, null=True, blank=True)
    institute = models.CharField(max_length=100, null=True, blank=True)
    yearfrom = models.IntegerField(null=True, blank=True)
    yearto = models.IntegerField(null=True, blank=True)
    grade = models.CharField(max_length=100, null=True, blank=True)

    class Meta:
        db_table = 'profileeducation'


class ProfileExperience(models.Model):
    id = models.AutoField(primary_key=True)
    profileid = models.IntegerField(null=True, blank=True)
    sequence = models.IntegerField(null=True, blank=True)
    jobtitle = models.CharField(max_length=100, null=True, blank=True)
    company = models.CharField(max_length=100, null=True, blank=True)
    yearfrom = models.IntegerField(null=True, blank=True)
    yearto = models.IntegerField(null=True, blank=True)

    class Meta:
        db_table = 'profileexperience'


class ProfileSkills(models.Model):
    id = models.AutoField(primary_key=True)
    profileid = models.IntegerField(null=True, blank=True)
    primaryskills = models.CharField(max_length=256, null=True, blank=True)
    secondaryskills = models.CharField(max_length=256, null=True, blank=True)

    class Meta:
        db_table = 'profileskills'


class ProfileProjects(models.Model):
    id = models.AutoField(primary_key=True)
    profileid = models.IntegerField(null=True, blank=True)
    sequence = models.IntegerField(null=True, blank=True)
    projectname = models.CharField(max_length=100, null=True, blank=True)
    clientname = models.CharField(max_length=100, null=True, blank=True)
    roleplayed = models.CharField(max_length=100, null=True, blank=True)
    skillsused = models.CharField(max_length=100, null=True, blank=True)
    yearsfrom = models.IntegerField(null=True, blank=True)
    yearsto = models.IntegerField(null=True, blank=True)

    class Meta:
        db_table = 'profileprojects'


class ProfileActivity(models.Model):
    id = models.AutoField(primary_key=True)
    profileid = models.IntegerField(null=True, blank=True)
    datentime = models.DateTimeField(null=True, blank=True)
    sequence = models.IntegerField(null=True, blank=True)
    activitycode = models.CharField(max_length=3, null=True, blank=True) #"PC - Profile Created | PS - Profile Screened | P1 - Profile Screening - Promoted | PC - Profile Coding Test | P2 - Profile Coding Test - Promoted | WE - Welcome Email Sent"
    acvityuserid = models.IntegerField(null=True, blank=True)
    activityname= models.CharField(null=True, blank=True, max_length=100)
    activityremarks = models.CharField(null=True, blank=True, max_length=200)
    activitystatus= models.CharField(null=True, blank=True, max_length=100)
    companyid= models.IntegerField(null=True, blank=True)

    class Meta:
        db_table = 'profileactivity'


class ProfileAwards(models.Model):
    id = models.AutoField(primary_key=True)
    profileid = models.IntegerField(null=True, blank=True)
    sequence = models.IntegerField(null=True, blank=True)
    awardname = models.CharField(max_length=100, null=True, blank=True)
    year = models.IntegerField(null=True, blank=True)

    class Meta:
        db_table = 'profileawards'   


class ProfileCertificates(models.Model):
    id = models.AutoField(primary_key=True)
    profileid = models.IntegerField(null=True, blank=True)
    certname = models.CharField(max_length=100, null=True, blank=True)
    sequence = models.IntegerField(null=True, blank=True)
    year = models.IntegerField(null=True, blank=True)

    class Meta:
        db_table = 'profilecertificates'   


class ProfileAddress(models.Model):
    id = models.AutoField(primary_key=True)
    profileid = models.IntegerField(null=True, blank=True)
    addline1 = models.CharField(max_length=100, null=True, blank=True)
    addline2 = models.CharField(max_length=100, null=True, blank=True)
    city = models.CharField(max_length=100, null=True, blank=True)
    state = models.CharField(max_length=40, null=True, blank=True)
    country = models.CharField(max_length=40, null=True, blank=True)
    zipcode = models.CharField(max_length=20, null=True, blank=True)

    class Meta:
        db_table = 'profileaddress'   




class ProfileAnalysis(models.Model):
    id = models.AutoField(primary_key=True)
    companyid = models.IntegerField(null=True)
    day = models.IntegerField(null=True, blank=True)
    month = models.IntegerField(null=True, blank=True)
    year = models.IntegerField(null=True, blank=True)
    userid = models.IntegerField(null=True)
    activitycode = models.CharField(max_length=3, null=True, blank=True)
    profilescount = models.IntegerField(null=True, blank=True)

    class Meta:
        db_table = 'profileanalysis'


class Workspace(models.Model):
    id = models.AutoField(primary_key=True)
    clientid = models.IntegerField(null=True, blank=True)
    project = models.CharField(max_length=100, null=True, blank=True)
    startdate = models.DateTimeField(null=True, blank=True)
    notes = models.CharField(max_length=100, null=True, blank=True)
    createdby = models.IntegerField(null=True, blank=True)
    createdat = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=1, null=True)
    jd_ids = models.JSONField(null=True)

    class Meta:
        db_table = 'workspace'


class Client(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, null=True, blank=True)
    companyid = models.IntegerField(null=True, blank=True)
    createdat = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=1, null=True)

    class Meta:
        db_table = 'client'
        
        
class jdlibrary(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=350, null=True)
    description = models.CharField(max_length=3024, null=True)
    role = models.CharField(max_length=50)
    min_exp = models.IntegerField()
    max_exp = models.IntegerField()
    primary_skills =models.CharField(max_length=2048, null=True)
    secondary_skills = models.CharField(max_length=2048, null=True)
    work_location =  models.CharField(max_length=512, null=True)
    
    
    class Meta:
        db_table = 'jdlibrary'


class JobBoard(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, null=True, blank=True)
    logo_path = models.CharField(max_length=100, null=True, blank=True)
    status = models.CharField(max_length=1, null=True, blank=True)

    class Meta:
        db_table = 'jobboard'


class JobBoardCredential(models.Model):
    id = models.AutoField(primary_key=True)
    companyid = models.IntegerField(null=True, blank=True)
    jobboardid = models.IntegerField(null=True, blank=True)
    apikey = models.CharField(max_length=512, null=True, blank=True)
    endpoint = models.CharField(max_length=512, null=True, blank=True)
    username = models.CharField(max_length=100, null=True, blank=True)
    password = models.CharField(max_length=100, null=True, blank=True)
    status = models.CharField(max_length=1, null=True, blank=True)

    class Meta:
        db_table = 'jobboardcredential'


class JDJobBoards(models.Model):
    id = models.AutoField(primary_key=True)
    companyid = models.IntegerField(null=True, blank=True)
    jobdescid = models.IntegerField(null=True, blank=True)
    jobboardid = models.IntegerField(null=True, blank=True)
    publishedon = models.DateTimeField(null=True, blank=True)
    publishedby = models.IntegerField(null=True, blank=True)
    status = models.CharField(max_length=1, null=True, blank=True)

    class Meta:
        db_table = 'jdjobboard'


class ResumeTemplate(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=40,null=True, blank=True)
    thumbnail = models.CharField(max_length=100,null=True, blank=True)
    filename = models.CharField(max_length=100,null=True, blank=True) 
    default_template = models.CharField(max_length=1,null=True, blank=True)
    status = models.CharField(max_length=1, null=True, blank=True)

    class Meta:
        db_table = 'resumetemplate'

