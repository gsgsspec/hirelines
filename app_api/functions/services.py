import json
import requests
import string
import secrets
import ast
from django.db.models import Q
from datetime import datetime, timedelta
from django.utils import timezone
from django.shortcuts import redirect
from urllib.parse import urljoin
from rest_framework.authtoken.models import Token
from .constants import public_email_domains
from hirelines.metadata import getConfig
from .mailing import sendRegistrainMail
from app_api.models import CompanyData, JobDesc, Candidate, Registration, ReferenceId, Company, User, User_data, RolesPermissions, Workflow, CallSchedule, \
    Vacation, WorkCal, ExtendedHours, HolidayCal
from app_api.functions.database import saveJdNewTest, saveAddJD, saveUpdateJd


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


def jdTestAdd(jdData,compyId):
    try:
        if jdData:  
            test_data = saveJdNewTest(jdData,compyId)
            return test_data
    except Exception as e:
        raise


def addJdServices(addjdData,companyID,hrEmail):
    try:
        saveAddJD(addjdData,companyID,hrEmail)
    except Exception as e:
        raise


def updateJdServices(addjdData,companyID,hrEmail):
    try:
        saveUpdateJd(addjdData,companyID,hrEmail)
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


def getCompanyJdData(cid):
    try:
        company_jds = JobDesc.objects.filter(companyid=cid,status='O')

        jds_list = []

        if company_jds:

            for jd in company_jds:

                jds_list.append({
                    'id': jd.id,
                    'title': jd.title
                })

        return jds_list

    except Exception as e:
        raise


def getCompanyJDsList(companyId):
    try:
        company_jds = JobDesc.objects.filter(companyid=companyId, status='O').values()
        return company_jds
    except Exception as e:
        raise


def jdDetails(jdId):
    try:
        jdData = JobDesc.objects.filter(id=jdId).last()
        return jdData
    except Exception as e:
        raise


def workFlowDataService(data,cmpyId):
    try:
        papersDetails = Workflow.objects.filter(jobid = data).values()
        return list(papersDetails)
    except Exception as e:
        raise

def getJdWorkflowService(jid,cid):
    try:

        jd_workflows = Workflow.objects.filter(jobid=jid,companyid=cid).order_by('order')

        workflow_data = []

        if jd_workflows:
            for workflow in jd_workflows:
                workflow_data.append({
                    'id':workflow.id,
                    'papertype':workflow.papertype,
                    'title': workflow.papertitle,
                    'paperid':workflow.paperid
                })

        return workflow_data
    
    except Exception as e:
        raise



def getCallScheduleDetails(cid):
    try:
        candidate = Candidate.objects.get(id=cid)

        jd = JobDesc.objects.get(id=candidate.jobid)

        jd_interviewers = ast.literal_eval(jd.interviewers)

        job_interviewers = []

        for job_interviewer in jd_interviewers:

            interviewer = User.objects.get(id=job_interviewer)
            job_interviewers.append({'id':interviewer.id,'name':interviewer.name})


        candidate_data = {
            'cid':candidate.id,
            'c_name': f"{candidate.firstname} {candidate.lastname}",
            'c_email': candidate.email,
            'c_mobile': candidate.mobile
        }

        return job_interviewers, candidate_data

    except Exception as e:
        raise



def interviewSchedulingService(aplid,int_id):
    try:

        call_scheduling_constraints = getConfig()['CALL_SCHEDULING_CONSTRAINTS']

        WORK_HOURS = int(call_scheduling_constraints["work_hours"])
        STARTING_HOUR = int(call_scheduling_constraints["starting_hour"])
        BLOCK_HOURS = int(call_scheduling_constraints["block_hours"])
        FREQUENCY = int(call_scheduling_constraints["frequency_mins"])
        
        basedt = datetime.today().replace(hour=STARTING_HOUR, minute=00, second=00, microsecond=00)

        scheduling_data = []

        scheduled_calls = list(CallSchedule.objects.filter(Q(status='S')|Q(status='R')).values_list('datentime', 'interviewerid'))
        scheduled_calls_list = []
        for scheduled_call in scheduled_calls:
            if scheduled_call[0]:
                scheduled_calls_list.append([scheduled_call[0].strftime("%Y-%m-%d %I:%M %p"), scheduled_call[1]])

        vacation_data = Vacation.objects.filter(empid=int_id).values("empid", "fromdate", "todate")
        workcal_data = WorkCal.objects.filter(empid=int_id).values()

        alter_timings_data = ExtendedHours.objects.filter(empid=int_id,status="A").values()
        alter_timings_dates_list = []
        alter_timings_list = {}

        for alter_timings in alter_timings_data:
            
            alter_dates_ = [[alter_timings["fromdate"] + timedelta(days=x),alter_timings["starttime"],alter_timings["workhours"],alter_timings["empid"]] for x in range((alter_timings["todate"]-alter_timings["fromdate"]).days + 1)]
            for alter_date in alter_dates_:
                formated_alter_date= alter_date[0].strftime("%a-%d-%b-%Y")
                alter_timings_dates_list.append(formated_alter_date)
                alter_timings_list[str(alter_date[0].strftime("%Y-%m-%d"))] = [alter_date[0],alter_date[1],alter_date[2],alter_date[3]]
        
        for x in range(0, 15): #days
            hours_list = []
            slots_list = []
            status_list = []

            telecallers = list(User.objects.filter(status='A', id=int_id).values_list('id', flat=True))

            _date = (basedt + timedelta(days=x)).strftime("%Y-%m-%d")
            _datetime = datetime.strptime(
                (basedt.replace(hour=00, minute=00, second=00, microsecond=00) + timedelta(days=x)).strftime(
                    "%Y-%m-%d %H:%M:%S"), "%Y-%m-%d %H:%M:%S")
            date_formated = (basedt + timedelta(days=x)).strftime("%a-%d-%b-%Y")
            for vacation in vacation_data:
                from_date = datetime.strptime(str(vacation['fromdate']), "%Y-%m-%d")
                to_date = datetime.strptime(str(vacation['todate']), "%Y-%m-%d")
                if from_date <= _datetime <= to_date:
                    if vacation['empid'] in telecallers: telecallers.remove(vacation['empid'])
            # for alter_hours in 
            for work_data in workcal_data:
                # print("work_data['weekoff1']",work_data['weekoff1'],date_formated,alter_timings_dates_list)
                if (work_data['weekoff1'] == date_formated.split("-")[0]) and (date_formated not in alter_timings_dates_list):
                    if work_data['empid'] in telecallers: telecallers.remove(work_data['empid'])
                if work_data['weekoff2'] == date_formated.split("-")[0] and (date_formated not in alter_timings_dates_list):
                    if work_data['empid'] in telecallers: telecallers.remove(work_data['empid'])
            for i in range(0, WORK_HOURS*2):  # (0,24) 24 means 12 Hours
                slot_time = basedt + timedelta(minutes=30 * i)
                curr_time = datetime.now().replace(second=00)# + datetime.timedelta(hours=4)
                hours_list.append(slot_time.strftime("%I:%M %p"))
                if (_date == datetime.today().strftime("%Y-%m-%d")) and (
                        slot_time <= (curr_time + timedelta(hours=BLOCK_HOURS, minutes=30))):
                    status_list.append("Blocked")
                    slots_list.append([])
                else:

                    occupied_tc = []

                    tc = telecallers
                    telecallers_set = set(tc)
                    for slot in scheduled_calls_list: 

                        if slot[0] == _date + " " + slot_time.strftime("%I:%M %p"):
                            
                            if slot[1] in tc:
                                occupied_tc.append(slot[1])

                    available_tc_list = list(telecallers_set.difference(set(occupied_tc)))
                    for work_data in workcal_data:
                        
                        slot_date = datetime.strptime(_date, "%Y-%m-%d").date()
                        slot_date_str = str(slot_date.strftime("%Y-%m-%d"))
                        
                        if slot_date_str in alter_timings_list:
                            alter_data = alter_timings_list[slot_date_str]
                            start_datetime = datetime.combine(datetime.date.today(), alter_data[1])
                            if len(str(alter_data[2]).split('.'))==2:
                                work_hours = int(alter_data[2].split(".")[0])
                                if work_hours-1 > ((WORK_HOURS*2)/2):
                                    work_hours = ((WORK_HOURS*2)/2)-1
                                work_mins = 30
                            else:
                                work_hours = int(alter_data[2])
                                if work_hours > ((WORK_HOURS*2)/2):
                                    work_hours = ((WORK_HOURS*2)/2)
                                work_mins = 0
                            
                            end_datetime = start_datetime + timedelta(hours=work_hours,minutes=work_mins)
                            end_time = end_datetime.time()
                            
                            if alter_data[1] > slot_time.time():
                                
                                if alter_data[3] in available_tc_list:
                                    available_tc_list.remove(alter_data[3])

                            if slot_time.time() >= end_time:
                                if alter_data[3] in available_tc_list:
                                    available_tc_list.remove(alter_data[3])
                        
                        else:
                            start_datetime = datetime.combine(datetime.date.today(), work_data['starttime'])
                            if len(work_data['workhours'].split('.'))==2:
                                work_hours = int(work_data['workhours'].split(".")[0])
                                if work_hours-1 > ((WORK_HOURS*2)/2):
                                    work_hours = ((WORK_HOURS*2)/2)-1
                                work_mins = 30
                            else:
                                work_hours = int(work_data['workhours'])
                                if work_hours > ((WORK_HOURS*2)/2):
                                    work_hours = ((WORK_HOURS*2)/2)
                                work_mins = 0
                            
                            end_datetime = start_datetime + timedelta(hours=work_hours,minutes=work_mins)
                            end_time = end_datetime.time()
                            
                            if work_data['starttime'] > slot_time.time():
                                
                                if work_data['empid'] in available_tc_list:
                                    available_tc_list.remove(work_data['empid'])

                            if slot_time.time() >= end_time:
                                if work_data['empid'] in available_tc_list:
                                    available_tc_list.remove(work_data['empid'])

                    if not available_tc_list:
                        status_list.append("No_Vacancy")
                    else:
                        status_list.append("Available")
                    slots_list.append(available_tc_list)
                if HolidayCal.objects.filter(holidaydt=_date).exists():
                    status_list = []
                    while len(status_list) <= WORK_HOURS * 2:
                        status_list.append("Holiday")
                        
            ids = []
            for slo in slots_list:
                ids.append(list(slo))
                
            dataObj = {
                "day": date_formated,
                "hours_list": hours_list,
                "slots_list": slots_list,
                "status": status_list,
                "ids": ids
            }
            scheduling_data.append(dataObj)

        return scheduling_data

    except Exception as e:
        raise



def getInterviewerCandidates(userid):
    try:

        call_details = CallSchedule.objects.filter(interviewerid=userid,status='S').order_by("-id")
        candidates = []

        for call_data in call_details:

            candidate = Candidate.objects.get(id=call_data.candidateid)
            jd = JobDesc.objects.get(id=candidate.jobid)

            candidates.append({
                'id': candidate.id,
                'name': f"{candidate.firstname} {candidate.lastname}",
                "scheduled_time" : call_data.datentime.strftime("%d-%b-%Y %I:%M %p"),
                "email": candidate.email,
                "c_code":candidate.candidateid,
                "jd" : jd.title,
                'scd_id':call_data.id
            })

        return candidates
    except Exception as e:
        raise


def getCandidateInterviewData(scd_id):
    try:

        resp = {
            'job_desc_data': None,
            'candidate_data':None,
        }

        acert_domain = getConfig()['DOMAIN']['acert']
        endpoint = '/api/candidate-interviewdata'

        url = urljoin(acert_domain, endpoint)

        call_details = CallSchedule.objects.get(id=scd_id)
        candidate = Candidate.objects.get(id=call_details.candidateid)
        candidate_data = {
            'c_code' : candidate.candidateid,
            'int_paperid': call_details.paper_id
        }

        send_candidate_data = requests.post(url, json = candidate_data)

        job_desc = JobDesc.objects.get(id=candidate.jobid)

        job_desc_data = {
            'jd_title':job_desc.title,
            'role': job_desc.role,
            'location':job_desc.location,
            'skills':job_desc.skillset,
            'notes':job_desc.skillnotes
        }

        int_paper_title = Workflow.objects.filter(paperid=call_details.paper_id).last().papertitle

        candidate_data = {
            'name': f"{candidate.firstname} {candidate.lastname}" ,
            'mobile': candidate.mobile,
            'email': candidate.email,
            'int_paper': int_paper_title if int_paper_title else 'N/A'
        }

        resp['job_desc_data'] = job_desc_data
        resp['candidate_data'] = candidate_data

        return resp

    except Exception as e:
        raise