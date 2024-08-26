import json
import requests
import string
import secrets
from datetime import datetime, timedelta
from django.utils import timezone
from django.shortcuts import redirect
from urllib.parse import urljoin
from rest_framework.authtoken.models import Token
from .constants import public_email_domains
from hirelines.metadata import getConfig
from .mailing import sendRegistrainMail
from app_api.models import CompanyData, JobDesc, Candidate, Registration, ReferenceId, Company, User, User_data, RolesPermissions



def addCompanyDataService(dataObjs):
    try:

        bussiness_email = str(dataObjs['reg-bemail'])

        email_domain = bussiness_email.split('@')[1]

        if email_domain in public_email_domains:
            return 1
        
        email_check = CompanyData.objects.filter(companyemail=bussiness_email)

        if email_check:
            return 2

        company_data = CompanyData(
            companyname = dataObjs["reg-company"],
            companyemail = bussiness_email,
            location = dataObjs['reg-location'],
            contactperson = dataObjs["reg-name"],
            companytype = dataObjs["reg-companytype"],
            registerationtime = datetime.now()
        )
        company_data.save()
        
        return 0


    except Exception as e:
        raise



def registerUserService(dataObjs):
    try:

        bussiness_email = str(dataObjs['reg-bemail'])

        user_email_domain = bussiness_email.split('@')[1]

        if user_email_domain in public_email_domains:
            return 1
        
        user_check = User.objects.filter(email=bussiness_email).last()

        if user_check:
            return 2

        company_check = Company.objects.filter(emaildomain=user_email_domain).last()

        random_password = generate_random_password()

        if company_check:
            user = User(
                name =  dataObjs["reg-name"],
                datentime = datetime.now(),
                location = dataObjs['reg-location'],
                companyid = company_check.id,
                role = "HR",
                password = random_password,
                email = bussiness_email,
                status = "A"
            )

            user.save()

        else:

            company = Company(
                name = dataObjs["reg-company"],
                emaildomain = user_email_domain,
                email = bussiness_email,
                companytype = dataObjs["reg-companytype"],
                registrationdate = datetime.now(),
                status = "T",
                freetrail = 'I'
            )

            company.save()

            user = User(
                name =  dataObjs["reg-name"],
                datentime = datetime.now(),
                location = dataObjs['reg-location'],
                companyid = company.id,
                role = "HR",
                password = random_password,
                email = bussiness_email,
                status = "A"
            )

            user.save()

            hirelines_domain = getConfig()['DOMAIN']['hirelines']

            mail_data = {'name':user.name,'email':user.email,'password':user.password,'url': f"{hirelines_domain}/login"}

            sendRegistrainMail(mail_data)

        return 0
            

    except Exception as e:
        raise


def getJobDescData(jid):
    try:

        job_desc = JobDesc.objects.filter(id=jid).last()

        if job_desc:

            screening_tests = Registration.objects.filter(companyid=1,jobid=jid,papertype='S').count()
            coding_tests = Registration.objects.filter(companyid=1,jobid=jid,papertype='E').count()
            interviews = Registration.objects.filter(companyid=1,jobid=jid,papertype='I').count()
            offer_letters = Registration.objects.filter(companyid=1,jobid=jid,papertype='I',status='O').count()

            jd_data = {
                'title' : job_desc.title,
                'screening_tests':screening_tests,
                'coding_tests':coding_tests,
                'interviews':interviews,
                'offer_letters':offer_letters
            }


            return jd_data


    except Exception as e:
        raise



def candidateRegistrationService(dataObjs):
    try:

        fname =  dataObjs['fname']
        lname =  dataObjs['lname']
        email =  dataObjs['email']
        mobile =  dataObjs['mobile']
        paper_id =  dataObjs['paper_id']
        company_id =  dataObjs['company_id']
        job_id = dataObjs['job_id']

        candidate = Candidate(
            firstname = fname,
            lastname = lname,
            companyid = company_id,
            paperid = paper_id,
            email = email,
            mobile = mobile,
            jobid = job_id,
            registrationdate = datetime.now(),
            status = 'P'
        )

        
        year = datetime.now().strftime("%y")

        refid_obj, refid_flag = ReferenceId.objects.get_or_create(type = "R", prefix1 = "{:03}".format(company_id), prefix2 = year)
            
        if refid_flag == True:
            lastid = 1
            refid_obj.lastid = lastid
            refid_obj.save()

        if refid_flag == False:
            lastid = refid_obj.lastid+1
            refid_obj.lastid = lastid
            refid_obj.save()

        candidate_id_seq = str('{:05}'.format(int(refid_obj.lastid)))
        candidate_code = f"{refid_obj.prefix1}{refid_obj.prefix2}{candidate_id_seq}"

        candidate.candidateid = candidate_code

        candidate.save()

        # Acert API

        acert_domain = getConfig()['DOMAIN']['acert']
        endpoint = '/api/hirelines-add-candidate'

        url = urljoin(acert_domain, endpoint)

        candidate_data = {'fname' : fname,'lname': lname, 'email':email, 'mobile': mobile, 'paper_id':paper_id, 'company_id':company_id, 'reference_id': candidate.candidateid}

        send_candidate_data = requests.post(url, json = candidate_data)
        
        response_content = send_candidate_data.content

        if response_content:
            json_data = json.loads(response_content.decode('utf-8'))

            c_registration = Registration(
                candidateid = candidate.id,
                paperid = candidate.paperid,
                registrationdate = candidate.registrationdate,
                status = 'P',
                companyid = candidate.companyid,
                jobid = candidate.jobid,
                papertype = json_data['data']
            )

            c_registration.save()


    except Exception as e:
        raise



def getJdCandidatesData(jid):
    try:   

        candidates = Candidate.objects.filter(jobid=jid,companyid=1)

        candidates_data = []

        for candidate in candidates:

            registrations = Registration.objects.filter(candidateid=candidate.id,companyid=candidate.companyid)

            candidate_info = {
                'id': candidate.id,
                'cid':candidate.candidateid,
                'name': candidate.firstname,
                'email': candidate.email,
                'registrations': {'S':[],'E':[],'I':[]}
            }

            for registration in registrations:

                registration_info = {
                    'date': registration.registrationdate.strftime("%Y-%m-%d"),
                    'status': registration.status,
                }

                if registration.papertype == 'S':
                    candidate_info['registrations']['S'].append(registration_info)
                elif registration.papertype == 'E':
                    candidate_info['registrations']['E'].append(registration_info)
                elif registration.papertype == 'I':
                    candidate_info['registrations']['I'].append(registration_info)

            candidates_data.append(candidate_info)

        return candidates_data

    except Exception as e:
        raise



def getCandidatesData():
    try:

        candidates_list = []

        candidates = Candidate.objects.all().order_by("-id")

        for candidate in candidates:

            candidates_list.append({
                'candidate_id': candidate.candidateid,
                'firstname': candidate.firstname,
                'lastname': candidate.lastname,
                'email' : candidate.email
            })

        return candidates_list

    except Exception as e:
        raise



def authentication_service(dataObjs):

    try:
        user = User.objects.get(email=dataObjs['email'],password=dataObjs['password'],status='A')

    except:
        return (None,)
    
    try:

        if user:
            check1 = User_data.objects.filter(usr_email=user.email, usr_password=user.password,user='C')
            
            if not check1:
                User_data(username=user.email, usr_email=user.email, usr_password=user.password, is_staff=True, user='C').save()
            token_obj = Token.objects.filter(user__usr_email=user.email).order_by('-created').first()
            user_data = User_data.objects.get(usr_email=user.email, usr_password=user.password,user='C')
            user_data.is_staff = True 
            user_data.save()
            if token_obj:
                return token_obj.key
            else:
                check = User_data.objects.filter(usr_email=user.email).first()
                token_obj, token_flag = Token.objects.get_or_create(user=check)
                return token_obj.key
    except Exception as e:
        print(str(e))
        raise



def get_functions_service(user_role):
    try:
        functions = RolesPermissions.objects.filter(enable__contains=user_role)
        temp = []

        for function in functions:
            
            functionObjList = [func for func in temp if
                               func['menuItemParent'] == function.function]
            if not functionObjList:
                uifuncObj = {
                    'menuItemParent': function.function,
                    'UIIcon': function.function_icon,
                    'menuItemKey': function.function_category,
                    'child': [],
                }
                uifuncObj['child'].append(
                    {'menuItemName': function.sub_function, 'menuItemLink': function.function_link})
                temp.append(uifuncObj)
            elif functionObjList:
                temp = [
                    menuItem for menuItem in temp if menuItem['menuItemParent'] != function.function]
                functionObjList[0]['child'].append(
                    {'menuItemName': function.sub_function, 'menuItemLink': function.function_link})
                temp.append(functionObjList[0])
        menuItemList = temp
        return menuItemList
    except Exception as e:
        print(str(e))
        raise



def checkCompanyTrailPeriod(user_mail):
    try:

        user = User.objects.filter(email=user_mail).last()

        if user:

            company = Company.objects.get(id=user.companyid)

            trial_days = getConfig()['FREETRAIL']['days']

            if company.freetrail == "I" and company.status == "T" :

                trial_end_date = company.registrationdate + timedelta(days=int(trial_days))

                if timezone.now() > trial_end_date:
                    
                    company.freetrail = "C"
                    company.save()
                    return True
                
            if company.freetrail == "C" and company.status == "T" :
        
                return True

    except Exception as e:
        raise 


def generate_random_password(length=15):
    try:
        characters = string.ascii_letters + string.digits

        password = ''.join(secrets.choice(characters) for _ in range(length))

        return password
    
    except Exception as e:
        raise