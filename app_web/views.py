from django.shortcuts import render, redirect
from django.contrib.auth import logout
from django.db.models import Q
from app_api.functions import constants
from app_api.functions.hashing import encrypt_code
from app_api.functions.masterdata import user_not_active,auth_user, get_current_path, getCompanyId
from app_api.models import User, Role, JobDesc, CallSchedule, Candidate, Company, Branding
from app_api.functions.services import getJobDescData, getCandidatesData, getJdCandidatesData, get_functions_service, checkCompanyTrailPeriod, getCompanyJdData, getCallScheduleDetails, \
    getInterviewerCandidates, getCandidateInterviewData, getCompanyJDsList,jdDetails, getCdnData, getInterviewCandidates, getInterviewFeedback, getCandidateWorkflowData
from app_api.functions.constants import hirelines_integration_script,hirelines_integration_function

from hirelines.metadata import getConfig
import json
import requests

domains = getConfig()['DOMAIN']
acert_domain = domains['acert']

def homePage(request):
    try:

        company_types = constants.company_types

        return render(request, "homepage.html", {'company_types': company_types})

    except Exception as e:
        raise



def webHomePage(request):
    try:

        company_types = constants.company_types

        return render(request, "web_index.html", {"template_name": 'web_page.html','company_types': company_types})

    except Exception as e:
        raise


def loginPage(request):
    try:

        return render(request, "web_index.html", {"template_name": 'login.html'})

    except Exception as e:
        raise


def registerPage(request):
    try:

        return render(request, "web_index.html", {"template_name": 'register.html'})

    except Exception as e:
        raise



def dashboardPage(request):
    if not request.user.is_active and not request.user.is_staff:
        return user_not_active(request, after_login_redirect_to=str(request.META["PATH_INFO"]))
    
    # if checkCompanyTrailPeriod(request.user):
    #     return redirect('/trial-expired')

    try:

        user_mail = request.user
        user_data = auth_user(user_mail)

        user_role = user_data.role

        menuItemList = get_functions_service(user_role)
        currentPath = get_current_path(request.path)
        

        menuItemObjList = [child for menuItemObj in menuItemList for child in menuItemObj['child'] if
                        child['menuItemLink'] == currentPath]

        if menuItemObjList:
            return render(request, "portal_index.html", {"template_name": "dashboard.html", 'menuItemList': menuItemList })
    
        else:
            return redirect('../')

    except Exception as e:
        raise



def emailTemplatesPage(request):
    if not request.user.is_active and not request.user.is_staff:
        return user_not_active(request, after_login_redirect_to=str(request.META["PATH_INFO"]))

    try:
        user_mail = request.user
        user_data = auth_user(user_mail)

        user_role = user_data.role

        menuItemList = get_functions_service(user_role)

        company_id = getCompanyId(user_mail)

        payload = {'company_id':company_id}

        url = f'{acert_domain}/api/emailtemp-list'
        
        api_res = requests.post(url, json=payload)
        data = json.loads(api_res.text)
        emailTemps = ''
        if data['statusCode'] == 0:
            emailTemps = data['data']

        return render(request, "portal_index.html", {"template_name": 'email_templates.html','menuItemList': menuItemList,
                                                     "emailTemps":emailTemps})

    except Exception as e:
        raise



def candidatesPage(request):
    if not request.user.is_active and not request.user.is_staff:
        return user_not_active(request, after_login_redirect_to=str(request.META["PATH_INFO"]))
    
    # if checkCompanyTrailPeriod(request.user):
    #     return redirect('/trial-expired')
    
    try:

        user_mail = request.user
        user_data = auth_user(user_mail)

        user_role = user_data.role

        menuItemList = get_functions_service(user_role)
        currentPath = get_current_path(request.path)

        menuItemObjList = [child for menuItemObj in menuItemList for child in menuItemObj['child'] if
                        child['menuItemLink'] == currentPath]

        candidates_data = getCandidatesData()

        if menuItemObjList:
            return render(request, "portal_index.html", {"template_name": 'candidates.html','menuItemList': menuItemList,"candidates_data" : candidates_data})

        else:
            return redirect('../')

    except Exception as e:
        raise



def reportsPage(request):

    if not request.user.is_active and not request.user.is_staff:
        return user_not_active(request, after_login_redirect_to=str(request.META["PATH_INFO"]))
    
    # if checkCompanyTrailPeriod(request.user):
    #     return redirect('/trial-expired')

    try:

        user_mail = request.user
        user_data = auth_user(user_mail)

        user_role = user_data.role

        menuItemList = get_functions_service(user_role)
        currentPath = get_current_path(request.path)

        menuItemObjList = [child for menuItemObj in menuItemList for child in menuItemObj['child'] if
                        child['menuItemLink'] == currentPath]

        job_descriptions = JobDesc.objects.all()
    
        if menuItemObjList: 
            return render(request, "portal_index.html", {"template_name": 'reports.html','menuItemList': menuItemList ,"job_descriptions":job_descriptions})
    
        else:
            return redirect('../')

    except Exception as e:
        raise
def jobDescription(request):
    if not request.user.is_active and not request.user.is_staff:
        return user_not_active(request, after_login_redirect_to=str(request.META["PATH_INFO"]))
    
    # if checkCompanyTrailPeriod(request.user):
    #     return redirect('/trial-expired')

    try:
        user_mail = request.user
        user_data = auth_user(user_mail)
        user_role = user_data.role

        menuItemList = get_functions_service(user_role)
        currentPath = get_current_path(request.path)

        menuItemObjList = [child for menuItemObj in menuItemList for child in menuItemObj['child'] if
                        child['menuItemLink'] == currentPath]
        if menuItemObjList:
            companyId = getCompanyId(user_mail)
            allJds = getCompanyJDsList(companyId)
            return render(request, "portal_index.html", {"template_name": "job_descriptions_list.html", 'menuItemList': menuItemList,'allJds':allJds})
        else:
            return redirect('../')

    except Exception as e:
        raise


# this function render's inside html pages
def Addjobdescription(request):
    if not request.user.is_active and not request.user.is_staff:
        return user_not_active(request, after_login_redirect_to=str(request.META["PATH_INFO"]))
    
    # if checkCompanyTrailPeriod(request.user):
    #     return redirect('/trial-expired')
    try:
        user_mail = request.user
        user_data = auth_user(user_mail)
        user_role = user_data.role

        menuItemList = get_functions_service(user_role)
        currentPath = get_current_path(request.path)

        menuItemObjList = [child for menuItemObj in menuItemList for child in menuItemObj['child'] if
                        child['menuItemLink'] == currentPath]
        
        return render(request, "portal_index.html", {"template_name": 'add_job_description.html', 'menuItemList': menuItemList})
    except Exception as e:
        raise

def update_jobdescription(request,update_jd_id):
    if not request.user.is_active and not request.user.is_staff:
        return user_not_active(request, after_login_redirect_to=str(request.META["PATH_INFO"]))
    
    # if checkCompanyTrailPeriod(request.user):
    #     return redirect('/trial-expired')
    try:
        user_mail = request.user
        user_data = auth_user(user_mail)
        user_role = user_data.role

        menuItemList = get_functions_service(user_role)
        currentPath = get_current_path(request.path)

        jd_details = jdDetails(update_jd_id)

        menuItemObjList = [child for menuItemObj in menuItemList for child in menuItemObj['child'] if
                        child['menuItemLink'] == currentPath]
        
        return render(request, "portal_index.html", {"template_name": 'update_job_description.html', 'menuItemList': menuItemList,'jd_details':jd_details})
    except Exception as e:
        raise

# this function render's inside html pages
def jobDescriptionSetUp(request,jd_id): 
    # if checkCompanyTrailPeriod(request.user):
    #     return redirect('/trial-expired')
    try:
        user_mail = request.user
        user_data = auth_user(user_mail)
        user_role = user_data.role

        menuItemList = get_functions_service(user_role)
        currentPath = get_current_path(request.path)
        jd_details = jdDetails(jd_id)
        enc_jdid = encrypt_code(jd_id)
        hirelines_integration_script_enc = hirelines_integration_script.replace("#enc_jdid#",enc_jdid)
        hirelines_integration_function_enc = hirelines_integration_function.replace("#enc_jdid#",enc_jdid)
        menuItemObjList = [child for menuItemObj in menuItemList for child in menuItemObj['child'] if
                        child['menuItemLink'] == currentPath]
        
        return render(request, "portal_index.html", {"template_name": 'jd_setup.html', 'menuItemList': menuItemList,'jd_details':jd_details,
                                                     "hirelines_integration_script_enc":hirelines_integration_script_enc,
                                                     "hirelines_integration_function_enc":hirelines_integration_function_enc})
    except Exception as e:
        raise


def brandingPage(request):
    if not request.user.is_active and not request.user.is_staff:
        return user_not_active(request, after_login_redirect_to=str(request.META["PATH_INFO"]))

    try:
        user_mail = request.user
        user_data = auth_user(user_mail)
        user_role = user_data.role

        menuItemList = get_functions_service(user_role)

        return render(request, "portal_index.html", {"template_name": 'branding.html','menuItemList': menuItemList})
    except Exception as e:
        raise


def addCandidatePage(request):
    # if checkCompanyTrailPeriod(request.user):
    #     return redirect('/trial-expired')
    try:

        user_mail = request.user
        user_data = auth_user(user_mail)
        user_role = user_data.role

        menuItemList = get_functions_service(user_role)
        company_id = getCompanyId(user_mail)

        jds_list = getCompanyJdData(company_id)

        return render(request, "portal_index.html", {"template_name": 'add_candidate.html','menuItemList': menuItemList,'jds_data':jds_list})

    except Exception as e:
        raise


def updateEmailTempPage(request, eid):
    if not request.user.is_active and not request.user.is_staff:
        return user_not_active(request, after_login_redirect_to=str(request.META["PATH_INFO"]))
    try:

        user_mail = request.user
        user_data = auth_user(user_mail)
        user_role = user_data.role

        menuItemList = get_functions_service(user_role)

        url = f'{acert_domain}/api/get-emailtemp-data'

        payload = {'id':eid}
        
        api_res = requests.post(url, json=payload)
        data = json.loads(api_res.text)
        emailTemps = ''
        if data['statusCode'] == 0:
            emailTemps = data['data']
        
        company_id = getCompanyId(user_mail)
        
        return render(request, "portal_index.html", {"template_name": 'update_emailtemp.html','menuItemList': menuItemList,
                                                     "emailTemps":emailTemps,"company_id":company_id})

    except Exception as e:
        raise



def jdDataPage(request, jid):
    # if checkCompanyTrailPeriod(request.user):
    #     return redirect('/trial-expired')
    try:

        jd_data = getJobDescData(jid)

        candidates_data = getJdCandidatesData(jid)

        return render(request, "portal_index.html", {"template_name": 'jd_data.html','jd_data':jd_data,'candidates_data':candidates_data})

    except Exception as e:
        raise


def trialExpired(request):
    try:

        return render(request, "trail_expired.html")

    except Exception as e:
        raise



def interviewCandidatesList(request):
    if not request.user.is_active and not request.user.is_staff:
        return user_not_active(request, after_login_redirect_to=str(request.META["PATH_INFO"]))
    
    # if checkCompanyTrailPeriod(request.user):
    #     return redirect('/trial-expired')
    try:

        user_mail = request.user
        user_data = auth_user(user_mail)

        user_role = user_data.role

        menuItemList = get_functions_service(user_role)
        currentPath = get_current_path(request.path)

        menuItemObjList = [child for menuItemObj in menuItemList for child in menuItemObj['child'] if
                        child['menuItemLink'] == currentPath]
        
        interview_candidates = getInterviewerCandidates(user_data.id)

        if menuItemObjList: 

            return render(request, "portal_index.html", {"template_name": 'interview_candidates.html','menuItemList': menuItemList,'interview_candidates':interview_candidates })
        
        else:
            return redirect('../')

    except Exception as e:
        raise


def candidateInterview(request,sch_id):
    if not request.user.is_active and not request.user.is_staff:
        return user_not_active(request, after_login_redirect_to=str(request.META["PATH_INFO"]))
    
    # if checkCompanyTrailPeriod(request.user):
    #     return redirect('/trial-expired')
    try:

        interview_data = getCandidateInterviewData(sch_id)
        cdn_data = getCdnData()

        jd_data = interview_data['job_desc_data']
        candidate_data = interview_data['candidate_data']
        interv_sect_ques = interview_data['interview_data']
        screening_data = interview_data['screening_data']
        coding_data = interview_data['coding_data']

        return render(request, "portal_index.html", {"template_name": 'candidate_interview.html','jd_data':jd_data,'cdn_data':cdn_data,
            'sections_questions_lst' : interv_sect_ques["sections_questions_lst"],'interview_sections' : interv_sect_ques['sections_lst'],
            'candidate_data':candidate_data,'screening_data':screening_data,'coding_data':coding_data })

    except Exception as e:
        raise



def interviewSchedule(request,cid):
    if not request.user.is_active and not request.user.is_staff:
        return user_not_active(request, after_login_redirect_to=str(request.META["PATH_INFO"]))
    
    try:

        user_mail = request.user
        user_data = auth_user(user_mail)

        user_role = user_data.role

        menuItemList = get_functions_service(user_role)

        call_schedule_details = getCallScheduleDetails(cid)

        interviewers = call_schedule_details[0]
        candidate_data = call_schedule_details[1]
        
        return render(request, "portal_index.html", {"template_name": 'interview_schedule.html','menuItemList':menuItemList,'interviewers':interviewers,'candidate_data':candidate_data })
    
    except Exception as e:
        raise


def evaluationPage(request):
    if not request.user.is_active and not request.user.is_staff:
        return user_not_active(request, after_login_redirect_to=str(request.META["PATH_INFO"]))
    
    # if checkCompanyTrailPeriod(request.user):
    #     return redirect('/trial-expired')

    try:

        user_mail = request.user
        user_data = auth_user(user_mail)

        user_role = user_data.role
        user_company = user_data.companyid
        menuItemList = get_functions_service(user_role)
        currentPath = get_current_path(request.path)
        
        hide_reg_number = "Y"
        
        menuItemObjList = [child for menuItemObj in menuItemList for child in menuItemObj['child'] if
                        child['menuItemLink'] == currentPath]

        if menuItemObjList:
            return render(request, "portal_index.html", {"template_name": "evaluation.html", 'menuItemList': menuItemList,"user_company":user_company,"hide_reg_number":hide_reg_number })
    
        else:
            return redirect('../')

    except Exception as e:
        raise


def feedbacksPage(request):
    if not request.user.is_active and not request.user.is_staff:
        return user_not_active(request, after_login_redirect_to=str(request.META["PATH_INFO"]))
    
    try:

        user_mail = request.user
        user_data = auth_user(user_mail)

        user_role = user_data.role

        menuItemList = get_functions_service(user_role)

        interviewed_candidates = getInterviewCandidates(user_data.id)

        return render(request, "portal_index.html", {"template_name": 'feedback.html','menuItemList':menuItemList,'interviewed_candidates':interviewed_candidates })
    
    except Exception as e:
        raise


def interviewerFeedback(request,cid):
    if not request.user.is_active and not request.user.is_staff:
        return user_not_active(request, after_login_redirect_to=str(request.META["PATH_INFO"]))
    
    try:

        user_mail = request.user
        user_data = auth_user(user_mail)

        user_role = user_data.role

        menuItemList = get_functions_service(user_role)

        feedback_data = getInterviewFeedback(cid,user_data.id)

        return render(request, "portal_index.html", {"template_name": 'interviewer_feedback.html','menuItemList':menuItemList,'feedback_data':feedback_data })
    
    except Exception as e:
        raise


def candidateSideMeetingPage(request, room_id):
    try:

        current_url = request.build_absolute_uri()

        call = CallSchedule.objects.filter(meetinglink=current_url).last()

        if call:
            candidate = Candidate.objects.filter(id=call.candidateid).last()
            company_details = Company.objects.filter(id=candidate.companyid).last()
            branding_details = Branding.objects.filter(companyid=candidate.companyid).last()
            
            call_details = {
                "candidate_id" : call.candidateid,
                "schedule_id" : call.id,
                "callend_status" : str(call.callendflag) if call.callendflag else "N",
                'company_logo'   : branding_details.logourl,
                'company_name'   : company_details.name
            }

        return render(request, "candidate_call.html",{'call_details':call_details})
    except Exception as e:
        print(str(e))
        raise



def candidateData(request,cid):
    if not request.user.is_active and not request.user.is_staff:
        return user_not_active(request, after_login_redirect_to=str(request.META["PATH_INFO"]))
    
    try:

        user_mail = request.user
        user_data = auth_user(user_mail)

        user_role = user_data.role

        menuItemList = get_functions_service(user_role)

        candidatedata = getCandidateWorkflowData(cid)

        candidate_info = candidatedata['candidate_info']
        registrations_data = candidatedata['registrations_data']


        return render(request, "portal_index.html", {"template_name": 'candidate_data.html','menuItemList':menuItemList,
                                'candidate_info':candidate_info,'registrations_data':registrations_data})
    
    except Exception as e:
        raise