from django.shortcuts import render, redirect
from django.contrib.auth import logout
from django.db.models import Q
from app_api.functions import constants
from app_api.functions.enc_dec import encrypt_code
from app_api.functions.masterdata import user_not_active,auth_user, get_current_path, getCompanyId
from app_api.models import Credits, User, Role, JobDesc, CallSchedule, Candidate, Company, Branding, Profile,Source,ProfileExperience,ProfileSkills
from app_api.functions.services import ProfileScoringEngine, getCompanyCreditsUsageService, getJobDescData, getCandidatesData, getJdCandidatesData, get_functions_service, checkCompanyTrailPeriod, getCompanyJdData, getCallScheduleDetails, companyUserLst, \
    getInterviewerCandidates, getCandidateInterviewData, getCompanyJDsList,jdDetails, getCdnData, getInterviewCandidates, getInterviewFeedback, getCandidateWorkflowData, getCompanyData, getDashboardData, getCompanySourcesData, \
    getCompanyCandidateUploadData,getProfileDetailsService,getProfileactivityDetailsService, getResumeData, getProfileData,getSlotsAvailable
from app_api.functions.constants import hirelines_integration_script,hirelines_integration_function

from hirelines.metadata import getConfig
import json
import requests
from app_api.functions.email_resume import fetch_gmail_attachments
from  app_api.functions.enc_dec import decrypt_code

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

# def webHomePage(request):
#     try:

#         company_types = constants.company_types

#         return render(request, 'tmp_website.html' )

#     except Exception as e:
#         raise

import difflib

def diff_highlight(preset, user_code):
    def normalize_line(line):
        """Removes leading spaces for comparison but keeps the indentation intact"""
        return line.lstrip()

    def add_indentation(line, indentation):
        """Adds back the preserved indentation"""
        return f"{indentation}{line}"

    preset_lines = preset.strip().splitlines()
    user_lines = user_code.strip().splitlines()

    diff_result = []

    # Use difflib to align the lines and find differences
    differ = difflib.Differ()
    diff = list(differ.compare(preset_lines, user_lines))

    # Iterate through the diff result
    for line in diff:
        if line.startswith('  '):  # Unchanged line
            # Preserve the line as is
            diff_result.append(line[2:])
        elif line.startswith('- '):  # Line in preset but not in user_code
            # Skip lines that are missing in user_code
            continue
        elif line.startswith('+ '):  # Line in user_code but not in preset
            # Separate indentation and content
            user_line = line[2:]
            user_indentation = len(user_line) - len(user_line.lstrip())
            user_content = user_line.lstrip()

            # Highlight only the content (excluding indentation)
            highlighted_line = f'<span class="highlight">{user_content}</span>'
            diff_result.append(add_indentation(highlighted_line, ' ' * user_indentation))
        elif line.startswith('? '):  # Differences within a line (handled separately)
            # Skip these lines as they are part of the previous '+' or '-' lines
            continue

    return "\n".join(diff_result)


def loginPage(request):
    try:
             
    #     preset = """
    # def sum(a,b):
    #     try:

    #         # CODE HERE
    #         return sum_
    #     except Exception as e:
    #         raise"""
            
    #     user_code = """
    # def sum(a,b):
    #     try:
    #         sum_ = a  +b
    #         return sum_
    #     except Exception as e:
    #         raise"""
    #     highlighted_result = diff_highlight(preset, user_code)
    #     obj={
    #         "preset": preset.strip(),
    #         "user_code": user_code.strip(),
    #         "highlighted_result": highlighted_result
    #     }
    #     return render(request, "bk_code_diff.html",{"obj":obj})
        return render(request, "web_index.html", {"template_name": 'login.html'})
    except Exception as e:
        raise


def logout_view(request):
    
    logout(request)  

    return redirect('/login') 


def registerPage(request):
    try:

        return render(request, "web_index.html", {"template_name": 'register.html'})

    except Exception as e:
        raise



def dashboardPage(request):
    if not request.user.is_active and not request.user.is_staff:
        return user_not_active(request, after_login_redirect_to=str(request.META["PATH_INFO"]))
    
    try:

        user_mail = request.user
        user_data = auth_user(user_mail)

        user_role = user_data.role

        menuItemList = get_functions_service(user_role)
        currentPath = get_current_path(request.path)

        company_id = getCompanyId(request.user)
        
        dashboard_data = getDashboardData(company_id)

        menuItemObjList = [child for menuItemObj in menuItemList for child in menuItemObj['child'] if
                        child['menuItemLink'] == currentPath]

        if menuItemObjList:
            return render(request, "portal_index.html", {"template_name": "dashboard.html", 'menuItemList': menuItemList,'dashboard_data':dashboard_data })
    
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

        candidates_data = getCandidatesData(user_data.id)

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
            allJds = getCompanyJDsList(companyId,user_role)
            return render(request, "portal_index.html", {"template_name": "job_descriptions_list.html", 'menuItemList': menuItemList,'activeJd':allJds['activeJd'], 'inactiveJd': allJds['inactiveJd']})
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
        print("user_role",user_role)
        compyId = getCompanyId(user_mail)
        menuItemList = get_functions_service(user_role)
        currentPath = get_current_path(request.path)

        jd_details = jdDetails(update_jd_id, compyId)

        menuItemObjList = [child for menuItemObj in menuItemList for child in menuItemObj['child'] if
                        child['menuItemLink'] == currentPath]
        
        return render(request, "portal_index.html", {"template_name": 'update_job_description.html', 'menuItemList': menuItemList,'jd_details':jd_details,'user_role':user_role})
    except Exception as e:
        raise



# this function render's inside html pages
# def jobDescriptionSetUp(request,jd_id): 
#     try:
#         user_mail = request.user
#         user_data = auth_user(user_mail)
#         user_role = user_data.role
#         companyId = getCompanyId(user_mail)

#         menuItemList = get_functions_service(user_role)
#         currentPath = get_current_path(request.path)
#         jd_details = jdDetails(jd_id, companyId)
#         enc_jdid = encrypt_code(jd_id)
#         hirelines_integration_script_enc = hirelines_integration_script.replace("#enc_jdid#",enc_jdid)
#         hirelines_integration_function_enc = hirelines_integration_function.replace("#enc_jdid#",enc_jdid)
#         menuItemObjList = [child for menuItemObj in menuItemList for child in menuItemObj['child'] if
#                         child['menuItemLink'] == currentPath]
        
#         return render(request, "portal_index.html", {"template_name": 'jd_setup.html', 'menuItemList': menuItemList,'jd_details':jd_details,
#                                                      "hirelines_integration_script_enc":hirelines_integration_script_enc,
#                                                      "hirelines_integration_function_enc":hirelines_integration_function_enc})
#     except Exception as e:
#         raise


# this function render's inside html pages
def jobDescriptionSetUp(request,jd_id): 
    try:
        user_mail = request.user
        user_data = auth_user(user_mail)
        user_role = user_data.role
        companyId = getCompanyId(user_mail)

        menuItemList = get_functions_service(user_role)
        currentPath = get_current_path(request.path)
        jd_details = jdDetails(jd_id, companyId)
        enc_jdid = encrypt_code(jd_id)
        hirelines_integration_script_enc = hirelines_integration_script.replace("#enc_jdid#",enc_jdid)
        hirelines_integration_function_enc = hirelines_integration_function.replace("#enc_jdid#",enc_jdid)
        menuItemObjList = [child for menuItemObj in menuItemList for child in menuItemObj['child'] if
                        child['menuItemLink'] == currentPath]
        
        return render(request, "portal_index.html", {"template_name": 'jd_setup_new.html', 'menuItemList': menuItemList,'jd_details':jd_details,'companyId':companyId,
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
        user_email = user_data.email
        user_companyid = user_data.companyid
        menuItemList = get_functions_service(user_role)

        
        companyBranding = Branding.objects.filter(companyid=user_companyid ).first()
         
        if not companyBranding:
            companyBranding = Branding.objects.filter(companyid=0).first()

    
        return render(request, "portal_index.html", {"template_name": 'branding.html','menuItemList': menuItemList,
                                                     "companyBranding":companyBranding})

    except Exception as e:
        raise


def addCandidatePage(request):
    # if checkCompanyTrailPeriod(request.user):
    #     return redirect('/trial-expired')
    if not request.user.is_active and not request.user.is_staff:
        return user_not_active(request, after_login_redirect_to=str(request.META["PATH_INFO"]))
    
    try:

        user_mail = request.user
        user_data = auth_user(user_mail)
        user_role = user_data.role

        menuItemList = get_functions_service(user_role)
        company_id = getCompanyId(user_mail)

        jds_list = getCompanyJdData(company_id)

        sources_data = json.dumps(getCompanySourcesData(user_data.companyid))

        return render(request, "portal_index.html", {"template_name": 'add_candidate.html','menuItemList': menuItemList,'jds_data':jds_list,'sources_data':sources_data})

    except Exception as e:
        raise


def updateEmailTempPage(request, eid):
    if not request.user.is_active and not request.user.is_staff:
        return user_not_active(request, after_login_redirect_to=str(request.META["PATH_INFO"]))
    try:

        user_mail = request.user
        user_data = auth_user(user_mail)
        user_role = user_data.role
        user_email = user_data.email
        menuItemList = get_functions_service(user_role)

        url = f'{acert_domain}/api/get-emailtemp-data'

        payload = {'id':eid}
        
        api_res = requests.post(url, json=payload)
        data = json.loads(api_res.text)
        emailTemps = ''
        if data['statusCode'] == 0:
            emailTemps = data['data']
        
        company_id = getCompanyId(user_mail)
        company_id = encrypt_code(company_id)
        return render(request, "portal_index.html", {"template_name": 'update_emailtemp.html','menuItemList': menuItemList,
                                                     "emailTemps":emailTemps,"company_id":company_id,"user_email":user_email})

    except Exception as e:
        raise



def jdDataPage(request, jid):
    if not request.user.is_active and not request.user.is_staff:
        return user_not_active(request, after_login_redirect_to=str(request.META["PATH_INFO"]))
    try:

        user_mail = request.user
        user_data = auth_user(user_mail)
        user_role = user_data.role
        menuItemList = get_functions_service(user_role)
        company_id = getCompanyId(user_mail)

        jd_data = getJobDescData(jid,company_id)
        candidates_data = getJdCandidatesData(jid,user_data.id)

        return render(request, "portal_index.html", {"template_name": 'jd_data.html','menuItemList': menuItemList,
                        'jd_data':jd_data,'candidates_data':candidates_data})

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

        schedule_type = request.GET.get('status', 'N')

        interviewers = call_schedule_details[0]
        candidate_data = call_schedule_details[1]
        
        return render(request, "portal_index.html", {"template_name": 'interview_schedule.html','menuItemList':menuItemList,'interviewers':interviewers,'candidate_data':candidate_data,
                                                    'schedule_type':schedule_type })
    
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
                'company_logo'   : branding_details.logourl if branding_details.logourl else "",
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
        feedbacks_data = candidatedata['feedbacks_data']


        return render(request, "portal_index.html", {"template_name": 'candidate_data.html','menuItemList':menuItemList,'feedbacks_data':feedbacks_data,
                                'candidate_info':candidate_info,'registrations_data':registrations_data})
    
    except Exception as e:
        raise


def userLst(request):
    if not request.user.is_active and not request.user.is_staff:
        return user_not_active(request, after_login_redirect_to=str(request.META["PATH_INFO"]))
    
    try:
        user_mail = request.user
        user_data = auth_user(user_mail)
        companyId = getCompanyId(user_mail)
        user_role = user_data.role
        menuItemList = get_functions_service(user_role)
        usersData = companyUserLst(companyId)
        

        return render(request, "portal_index.html", {"template_name": 'usersLst.html','menuItemList':menuItemList
                                                     , 'usersDataLst':usersData['usrs'], 'rolesLst':usersData['roles']})
    
    except Exception as e:
        raise


def reportsPage(request):
    if not request.user.is_active and not request.user.is_staff:
        return user_not_active(request, after_login_redirect_to=str(request.META["PATH_INFO"]))
    
    try:

        user_mail = request.user
        user_data = auth_user(user_mail)

        companyId = getCompanyId(user_mail)

        user_role = user_data.role

        menuItemList = get_functions_service(user_role)

        return render(request, "portal_index.html", {"template_name": 'reports.html','menuItemList':menuItemList})
    
    except Exception as e:
        raise


def creditsUsageReportPage(request):
    if not request.user.is_active and not request.user.is_staff:
        return user_not_active(request, after_login_redirect_to=str(request.META["PATH_INFO"]))
    
    try:

        user_mail = request.user
        user_data = auth_user(user_mail)

        user_role = user_data.role

        menuItemList = get_functions_service(user_role)
        
        payload={"cid":user_data.companyid}
        credits_usage = getCompanyCreditsUsageService(payload)
        
        return render(request, "portal_index.html", {"template_name": 'credits_usage_report.html','menuItemList':menuItemList,
                                                     "credits_usage":credits_usage})
    
    except Exception as e:
        raise




def companyPage(request):
    if not request.user.is_active and not request.user.is_staff:
        return user_not_active(request, after_login_redirect_to=str(request.META["PATH_INFO"]))
    
    try:

        user_mail = request.user
        user_data = auth_user(user_mail)

        user_role = user_data.role

        menuItemList = get_functions_service(user_role)

        company_data = getCompanyData(user_data.companyid)

        company_types = constants.company_types
        
        return render(request, "portal_index.html", {"template_name": 'company_data.html','menuItemList':menuItemList,
                                                     'company_types':company_types,'company_data':company_data})
    
    except Exception as e:
        raise


def demoPage(request):
    try:
        
        demo_video = getConfig()['APP_CONFIG']['demo_videoid']

        return render(request, "web_index.html", {"template_name": 'demo.html','demo_video':demo_video})

    except Exception as e:
        raise



def termsAndConditionsPage(request):
    try:
        

        return render(request, "tnc.html")

    except Exception as e:
        raise


def privacyPolicyPage(request):
    try:
        

        return render(request, "privacy_policy.html")

    except Exception as e:
        raise



def sourcesPage(request):
    if not request.user.is_active and not request.user.is_staff:
        return user_not_active(request, after_login_redirect_to=str(request.META["PATH_INFO"]))
    
    try:

        user_mail = request.user
        user_data = auth_user(user_mail)

        user_role = user_data.role

        menuItemList = get_functions_service(user_role)

        sources_data = getCompanySourcesData(user_data.companyid)

        return render(request, "portal_index.html", {"template_name": 'sources.html','menuItemList':menuItemList,'sources_data':sources_data})
    
    except Exception as e:
        raise


def uploadCandidatesPage(request):
    if not request.user.is_active and not request.user.is_staff:
        return user_not_active(request, after_login_redirect_to=str(request.META["PATH_INFO"]))
    
    try:

        user_mail = request.user
        user_data = auth_user(user_mail)

        user_role = user_data.role

        menuItemList = get_functions_service(user_role)
        company_id = getCompanyId(user_mail)

        jds_list = getCompanyJdData(company_id)
        sources_data = json.dumps(getCompanySourcesData(user_data.companyid))

        candidates_upload_data = getCompanyCandidateUploadData(company_id)

        # print('candidates_upload_data',candidates_upload_data)
        
        return render(request, "portal_index.html", {"template_name": 'candidate_upload.html','menuItemList':menuItemList,'sources_data':sources_data,
                                                     'jds_data':jds_list,'candidates_upload_data':candidates_upload_data})
    
    except Exception as e:
        raise


def profilesPage(request):
    if not request.user.is_active and not request.user.is_staff:
        return user_not_active(request, after_login_redirect_to=str(request.META["PATH_INFO"]))

    try:
        user_mail = request.user
        user_data = auth_user(user_mail)
        print("user_data",user_data)
        user_role = user_data.role
        print("user_role",user_role)

        menuItemList = get_functions_service(user_role)
        currentPath = get_current_path(request.path)

        menuItemObjList = [
            child for menuItemObj in menuItemList
            for child in menuItemObj["child"]
            if child["menuItemLink"] == currentPath
        ]

        # Simple: Convert queryset → list of dictionaries
        profile_details = list(Profile.objects.filter(companyid=user_data.companyid).values())
        source_list=list(Source.objects.filter(companyid=user_data.companyid).values())

        #  Add source name + status text
        for p in profile_details:
            # Source
            src = Source.objects.filter(id=p["sourceid"]).first()
            p["source_code"] = src.label if src else ""

            # Status
            status_map = {
                "D": "Draft",
                "R": "Rejected",
                "O": "Offered",
                "E": "Employee"
            }
            p["status_text"] = status_map.get(p["status"], "NA")

            if p.get("dateofcreation"):
                p["formatted_date"] = p["dateofcreation"].strftime("%d-%b-%Y %I:%M %p")
            else:
                p["formatted_date"] = ""

            exp = ProfileExperience.objects.filter(profileid=p["id"]).values("yearfrom", "yearto").first()

            if exp:
                year_from = int(exp["yearfrom"])
                year_to = int(exp["yearto"])

                total_exp = year_to - year_from  

                p["final_experience"] = f"{total_exp} Years"
            else:
                p["final_experience"] = "0 Years"

            skills = ProfileSkills.objects.filter(profileid=p["id"]).values(
                "primaryskills", "secondaryskills"
            ).first()

            if skills:
                p["primaryskills_name"] = skills.get("primaryskills", "")
                p["secondaryskills_name"] = skills.get("secondaryskills", "")
            else:
                p["primaryskills_name"] = ""
                p["secondaryskills_name"] = ""



        if menuItemObjList:
            return render(
                request,
                "portal_index.html",
                {
                    "template_name": "profiles.html",
                    "menuItemList": menuItemList,
                    "profile_details": profile_details,
                    "source_list":source_list  
                },
            )
        else:
            return redirect("../")

    except Exception as e:
        raise





def profileviewPage(request,pid):
    if not request.user.is_active and not request.user.is_staff:
        return user_not_active(request, after_login_redirect_to=str(request.META["PATH_INFO"]))
    
    try:
        user_mail = request.user
        user_data = auth_user(user_mail)

        user_role = user_data.role

        menuItemList = get_functions_service(user_role)

        profile_details=getProfileDetailsService(pid)
       

        return render(request, "portal_index.html", {"template_name": 'profileview.html','menuItemList': menuItemList,'profile_details':profile_details})

      
    except Exception as e:
        raise  


def profileactivityviewPage(request,pid):
    if not request.user.is_active and not request.user.is_staff:
        return user_not_active(request, after_login_redirect_to=str(request.META["PATH_INFO"]))
  

    try:

        user_mail = request.user
        user_data = auth_user(user_mail)

        user_role = user_data.role


        activity_details=getProfileactivityDetailsService(pid)


        menuItemList = get_functions_service(user_role)
        return render(request, "portal_index.html", {"template_name": 'profileactivity.html','menuItemList': menuItemList,"activity_details":activity_details})

   
    except Exception as e:
        raise
    

def resumeInboxPage(request):
    if not request.user.is_active and not request.user.is_staff:
        return user_not_active(request, after_login_redirect_to=str(request.META["PATH_INFO"]))
    
    try:
        user_mail = request.user
        user_data = auth_user(user_mail)

        user_role = user_data.role

        menuItemList = get_functions_service(user_role)

        # gmail_data = fetch_gmail_attachments()
        sources_data = getCompanySourcesData(user_data.companyid)

        resumes_data = getResumeData(user_data)

        return render(request, "portal_index.html", {"template_name": 'resume_inbox.html','menuItemList':menuItemList,
            "resumes_data":resumes_data, "user_data":user_data, "sources_data":sources_data
        })
      
    except Exception as e:
        raise   


def updateProfileDetailsPage(request, pid):
    if not request.user.is_active and not request.user.is_staff:
        return user_not_active(request, after_login_redirect_to=str(request.META["PATH_INFO"]))
    
    try:

        user_mail = request.user
        user_data = auth_user(user_mail)
       
        user_role = user_data.role

        menuItemList = get_functions_service(user_role)

        profile_data = getProfileData(pid, user_data)
        
        return render(request, "portal_index.html", {"template_name": 'update_profile.html','menuItemList':menuItemList,"profile_data":profile_data})
    
    except Exception as e:
        raise


def addProfilePage(request): 
    try:
        user_mail = request.user
        user_data = auth_user(user_mail)

        user_role = user_data.role

        menuItemList = get_functions_service(user_role)

        sources_data = json.dumps(getCompanySourcesData(user_data.companyid))

        return render(request, "portal_index.html", {"template_name": 'add_profile.html','menuItemList':menuItemList, "sources_data":sources_data})

    except Exception as e:
        raise
       

def view_resumePage(request,pid):
    
    try:
        user_mail = request.user
        user_data = auth_user(user_mail)

        user_role = user_data.role
        username=user_data.name
        comany_name=Company.objects.get(id=user_data.companyid).name


        menuItemList = get_functions_service(user_role)

        profile_details=getProfileDetailsService(pid)
        
        engine = ProfileScoringEngine()
        profile_strength = engine.score_profile(pid)
        print("profile_strength:\n",profile_strength)
        return render(request, "portal_index.html", {"template_name": 'view_resume.html','menuItemList': menuItemList,'profile_details':profile_details,"username": username,'comany_name':comany_name,
                                                     "profile_strength":profile_strength})
      
    except Exception as e:
        raise  





def workCalenderPage(request):
    try:
        user_mail = request.user
        print("user_mail",user_mail)
        user_data = auth_user(user_mail)
        print("user_data",user_data)
        user_id = user_data.id
        print("user_id",user_id)
        company_id = user_data.companyid
        print("company_id",company_id)

        user_role = user_data.role


        menuItemList = get_functions_service(user_role)

        return render(request, "portal_index.html", {"template_name": 'work_calender.html','menuItemList':menuItemList,'user_id':user_id, 'company_id':company_id})

    except Exception as e:
        raise
def scheduleInterviewPage(request, cid):
    try:
        
        deccrypt_cid = decrypt_code(cid)
        print("decrypt_cid",deccrypt_cid)
        
        # 1. Fetch the raw list of slots from the backend function
        slots_available_list, job_title, company_name,status = getSlotsAvailable(deccrypt_cid)
        
        
        # 2. Correct way to pass context: {string_key: python_variable_value}
        # The key 'slots_available' will be used in your HTML template ({{ slots_available|safe }})
        return render(request, "candidate_interview_schedule.html", {
            'slots_available': slots_available_list,'company_name': company_name , 'job_title': job_title , 'status': status
        })

    except Exception as e:
        # Proper error handling or logging here
        print(f"Error processing interview page for candidate {cid}: {e}")
        # Optionally render a safe error page instead of raising
        raise # Reraise the exception for development debugging
