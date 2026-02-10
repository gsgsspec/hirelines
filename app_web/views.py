from django.shortcuts import render, redirect
from django.contrib.auth import logout
from django.db.models import Q
from app_api.functions import constants
from app_api.functions.enc_dec import encrypt_code
from app_api.functions.masterdata import user_not_active,auth_user, get_current_path, getCompanyId
from app_api.models import Credits, User, Role, JobDesc, CallSchedule, Candidate, Company, Branding, Profile,Source,ProfileExperience,ProfileSkills,Lookupmaster, ProfileActivity,jdlibrary
from app_api.functions.services import getCompanyCreditsUsageService, getJobDescData, getCandidatesData, getJdCandidatesData, get_functions_service, checkCompanyTrailPeriod, getCompanyJdData, getCallScheduleDetails, companyUserLst, \
    getInterviewerCandidates, getCandidateInterviewData, getCompanyJDsList,jdDetails, getCdnData, getInterviewCandidates, getInterviewFeedback, getCandidateWorkflowData, getCompanyData, getDashboardData, getCompanySourcesData, \
    getCompanyCandidateUploadData,getProfileDetailsService,getProfileactivityDetailsService, getResumeData, getProfileData,getSlotsAvailable, getRecruitersData,getRecritmentDashboardData,getWorkspaces, getWorkspaceData, getCompanyClients,get_default_email_template_service,getHiringManagersData,companyClientLst,RecruitersPerformanceService, \
    getJobboards, getJDJobboards, getOverallDashboardCounts,SourcePerformanceService, getResumeTemplates
from app_api.functions.constants import hirelines_integration_script,hirelines_integration_function

from hirelines.metadata import getConfig
import json
import requests
from app_api.functions.email_resume import fetch_gmail_attachments
from  app_api.functions.enc_dec import decrypt_code


from datetime import datetime
from django.db.models.functions import Lower
from app_api.functions.constants import const_profile_status



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
        companyId = getCompanyId(user_mail)
        hiring_managers,current_user_id = getHiringManagersData(companyId,user_mail) 

        menuItemObjList = [child for menuItemObj in menuItemList for child in menuItemObj['child'] if
                        child['menuItemLink'] == currentPath]
        
        return render(request, "portal_index.html", {"template_name": 'add_job_description.html', 'menuItemList': menuItemList ,'hiring_managers':hiring_managers})
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
        recruiters_data = getRecruitersData(update_jd_id, compyId)
        hiring_managers,user_id = getHiringManagersData(compyId,user_mail)
        is_hiring_manager = False
        if jd_details and jd_details.get('hiringmanager'):
            is_hiring_manager = str(jd_details.get('hiringmanager')) == str(user_id)

        job_boards = getJDJobboards(user_data,update_jd_id)
        menuItemObjList = [child for menuItemObj in menuItemList for child in menuItemObj['child'] if
                        child['menuItemLink'] == currentPath]
        return render(request, "portal_index.html", {"template_name": 'update_job_description.html', 'menuItemList': menuItemList,'jd_details':jd_details,'user_role':user_role,'recruiters_data':recruiters_data,'hiring_managers':hiring_managers,'is_hiring_manager':is_hiring_manager,
                                                     "job_boards":job_boards})
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
        company_id = user_data.companyid

    
        companyBranding = Branding.objects.filter(companyid=user_companyid).first()
        
        email_template_data = get_default_email_template_service(company_id)
         
        if not companyBranding:
            companyBranding = Branding.objects.filter(companyid=0).first()

    
        return render(request, "portal_index.html", {"template_name": 'branding.html','menuItemList': menuItemList,
                                                     "companyBranding":companyBranding,"email_template_data":email_template_data})

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

        # sources_data = json.dumps(getCompanySourcesData(user_data.companyid))
        sources_data = getCompanySourcesData(user_data.companyid)

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
    
    try:

        interview_data = getCandidateInterviewData(sch_id)
        cdn_data = getCdnData()

        jd_data = interview_data['job_desc_data']
        candidate_data = interview_data['candidate_data']
        interv_sect_ques = interview_data['interview_data']
        screening_data = interview_data['screening_data']
        coding_data = interview_data['coding_data']
        profile_data = interview_data['profile_data']
        profiling_video = interview_data["profiling_video"]

        return render(request, "portal_index.html", {"template_name": 'candidate_interview.html','jd_data':jd_data,'cdn_data':cdn_data,
            'sections_questions_lst' : interv_sect_ques["sections_questions_lst"],'interview_sections' : interv_sect_ques['sections_lst'],'profile_data':profile_data,
            'candidate_data':candidate_data,'screening_data':screening_data,'coding_data':coding_data,'profiling_video':profiling_video })

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
        # sources_data = json.dumps(getCompanySourcesData(user_data.companyid))
        sources_data = getCompanySourcesData(user_data.companyid)

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
        profile_details = list(Profile.objects.filter(companyid=user_data.companyid).values().order_by("-dateofcreation"))
        source_list=list(Source.objects.filter(companyid=user_data.companyid).values())

        #  Add source name + status text
        for p in profile_details:
            # Source
            src = Source.objects.filter(id=p["sourceid"]).first()
            p["source_code"] = src.label if src else ""
            
            # p["profilestrength"]= p.get("strength", 0)
            p["profilestrength"] = p.get("strength") or 0
            # Status
            const_profile_status
            p["status_text"] = const_profile_status.get(p["status"], "NA")

            if p.get("dateofcreation"):
                p["formatted_date"] = p["dateofcreation"].strftime("%d-%b-%Y %I:%M %p")
            else:
                p["formatted_date"] = ""

            experience_list = (
            ProfileExperience.objects.filter(profileid=p["id"])
            .values("jobtitle", "company", "yearfrom", "yearto")
            .order_by("sequence")
        )
            total_exp = 0 
            for exp in experience_list:
                try:
                    yf = int(exp.get("yearfrom", 0))
                    yt = int(exp.get("yearto", 0))

                    if yt >= yf:
                        total_exp += yt - yf
                except:
                    pass

                p["final_experience"] = f"{total_exp} Years"

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
        
        return render(request, "portal_index.html", {"template_name": 'profile_view.html','menuItemList': menuItemList,'profile_details':profile_details})

      
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
        
        if activity_details:
            profileid = activity_details[0].get("profileid")
        else:
            profileid = pid   
        
        activity_names = Lookupmaster.objects.filter(lookupid=1,status='A').exclude(lookupmasterid=0).values_list('lookupname', flat=True)

        exists = ProfileActivity.objects.filter(
            profileid=pid,
            activitycode="E1"
        ).exists()

        if exists:
            email_exist="Y"
        else:
            email_exist="N"

        

        menuItemList = get_functions_service(user_role)
        return render(request, "portal_index.html", {"template_name": 'profileactivity.html','menuItemList': menuItemList,"activity_details":activity_details,"activity_names":activity_names,"email_exist":email_exist,'profileid':profileid})

   
    except Exception as e:
        raise
    

def resumeInboxPage(request):
    
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
        profileid = pid 

        user_mail = request.user
        user_data = auth_user(user_mail)
       
        user_role = user_data.role

        menuItemList = get_functions_service(user_role)

        profile_data = getProfileData(pid, user_data)
        profile_details=getProfileDetailsService(pid)
    
        
        return render(request, "portal_index.html", {"template_name": 'update_profile.html','menuItemList':menuItemList,"profile_data":profile_data,"profileid": profileid, "profile_details":profile_details})
    
    except Exception as e:
        raise


def addProfilePage(request): 
    try:
        user_mail = request.user
        user_data = auth_user(user_mail)

        user_role = user_data.role

        menuItemList = get_functions_service(user_role)

        # sources_data = json.dumps(getCompanySourcesData(user_data.companyid))
        sources_data = getCompanySourcesData(user_data.companyid)
        print("sources_data",sources_data)

        return render(request, "portal_index.html", {"template_name": 'add_profile.html','menuItemList':menuItemList, "sources_data":sources_data})

    except Exception as e:
        raise
       

def view_resumePage(request,pid):
    try:
        profileid = pid
        user_mail = request.user
        user_data = auth_user(user_mail)

        user_role = user_data.role
        username=user_data.name
        comany_name=Company.objects.get(id=user_data.companyid).name


        menuItemList = get_functions_service(user_role)

        profile_details=getProfileDetailsService(pid)

        
        return render(request, "portal_index.html", {"template_name": 'view_resume.html','menuItemList': menuItemList,'profile_details':profile_details,"username": username,'comany_name':comany_name,
                                                     "profile_strength":"",'profileid':profileid})
      
    except Exception as e:
        raise  



def workCalenderPage(request):
    try:
        user_mail = request.user
        user_data = auth_user(user_mail)
        user_id = user_data.id
        company_id = user_data.companyid

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

        call_scheduling_constraints = getConfig()["CALL_SCHEDULING_CONSTRAINTS"]

        BLOCK_HOURS = int(call_scheduling_constraints["block_hours"])
        
        # 2. Correct way to pass context: {string_key: python_variable_value}
        # The key 'slots_available' will be used in your HTML template ({{ slots_available|safe }})
        return render(request, "candidate_interview_schedule.html", {
            'slots_available': slots_available_list,'company_name': company_name , 'job_title': job_title , 'status': status , 'block_hours':BLOCK_HOURS
        })

    except Exception as e:
        # Proper error handling or logging here
        print(f"Error processing interview page for candidate {cid}: {e}")
        # Optionally render a safe error page instead of raising
        raise # Reraise the exception for development debugging



def recruiterdashboardPage(request):
    if not request.user.is_active and not request.user.is_staff:
        return user_not_active(request, after_login_redirect_to=str(request.META["PATH_INFO"]))
    
    try:

        user_mail = request.user
        user_data = auth_user(user_mail)

        user_role = user_data.role
        logged_recruiter_id = user_data.id      # current recruiter id


        menuItemList = get_functions_service(user_role)
        currentPath = get_current_path(request.path)

        company_id = getCompanyId(request.user)
        now = datetime.now()

        current_month_value = now.strftime('%Y-%m')       
        current_month_label = now.strftime('%B, %Y')  
        
        selected_recruiter = request.GET.get("recruiter")
        month_value = request.GET.get("month")

     
        if user_role == "Recruiter":
            recruiters = User.objects.filter(
                id=logged_recruiter_id,
                role="Recruiter",
                companyid=company_id
            ).order_by(Lower("name")).values("id", "name")
            show_all_option = False
        else:
            recruiters = User.objects.filter(
                role__in=["Recruiter", "HR-Admin"],
                companyid=company_id
            ).order_by(Lower("name")).values("id", "name")
            show_all_option = True


        recruitment_dashboard_data = getRecritmentDashboardData(
            company_id=company_id,
            user_role=user_role,
            logged_recruiter_id=logged_recruiter_id,
            selected_recruiter=selected_recruiter,
            month_value=month_value
        )
            


        menuItemObjList = [child for menuItemObj in menuItemList for child in menuItemObj['child'] if
                        child['menuItemLink'] == currentPath]

        if menuItemObjList:
            return render(request, "portal_index.html", {"template_name": "recruiter_dashboard.html", 'menuItemList': menuItemList,  "current_month_value": current_month_value,"current_month_label": current_month_label,"recruiters": recruiters,
            "show_all_option": show_all_option,**recruitment_dashboard_data

        })
    
        else:
            return redirect('../')

    except Exception as e:
        raise



def workspacePage(request):
    try:

        user_mail = request.user
        user_data = auth_user(user_mail)

        user_role = user_data.role

        menuItemList = get_functions_service(user_role)
        currentPath = get_current_path(request.path)

        menuItemObjList = [child for menuItemObj in menuItemList for child in menuItemObj['child'] if
                        child['menuItemLink'] == currentPath]
        

        workspaces = getWorkspaces(user_data)
        clients_data = getCompanyClients(user_data)
        # print("workspaces",workspaces)
        # print("clients_data",clients_data)
        # print("assign_jds",workspaces[1])
        
        if menuItemObjList:
            return render(request, "portal_index.html", {"template_name": "workspace.html", 'menuItemList': menuItemList, 'workspaces':workspaces[0],"assign_jds":workspaces[1],"user_name":user_data.name, "clients_data":clients_data })
        else:
            return redirect('../')

    except Exception as e:
        raise


def workspaceDetailsPage(request,wid):
    try:

        user_mail = request.user
        user_data = auth_user(user_mail)

        user_role = user_data.role

        menuItemList = get_functions_service(user_role)

        workspace_data =  getWorkspaceData(user_data,wid)
        print("workspace_data",workspace_data)

        return render(request, "portal_index.html", {"template_name": "workspace_data.html", 'menuItemList': menuItemList,"workspace_data":workspace_data })

    except Exception as e:
        raise





def clientLst(request):
    if not request.user.is_active and not request.user.is_staff:
        return user_not_active(request, after_login_redirect_to=str(request.META["PATH_INFO"]))
    
    try:
        user_mail = request.user
        user_data = auth_user(user_mail)
        companyId = getCompanyId(user_mail)
        user_role = user_data.role
        menuItemList = get_functions_service(user_role)
        clientData = companyClientLst(companyId)
        print("clientData",clientData)
                
        for client in clientData['usrs']:
            if client['createdat']:
                client['createdat'] = client['createdat'].strftime("%d-%b-%Y %I:%M %p")
            else:
                client['createdat'] = "-"


        return render(request, "portal_index.html", {"template_name": 'clientLst.html','menuItemList':menuItemList
                                                     , 'usersDataLst':clientData['usrs']})
    
    except Exception as e:
        raise
    

def recruiters_performance_reportPage(request):
    if not request.user.is_active and not request.user.is_staff:
        return user_not_active(request, after_login_redirect_to=str(request.META["PATH_INFO"]))
    
    try:

        user_mail = request.user
        user_data = auth_user(user_mail)

        user_role = user_data.role

        menuItemList = get_functions_service(user_role)
        
        payload={"cid":user_data.companyid}
        recruiters_performance = RecruitersPerformanceService(payload)


        
        return render(request, "portal_index.html", {"template_name": 'recruiters_performance_report.html','menuItemList':menuItemList,
                                                                     "recruiter_report": recruiters_performance["data"], "from_date": recruiters_performance["from_date"], "to_date": recruiters_performance["to_date"],
                                                                     })
    
    except Exception as e:
        raise




def jobBoardsPage(request):
    try:

        user_mail = request.user
        user_data = auth_user(user_mail)

        user_role = user_data.role

        menuItemList = get_functions_service(user_role)
        currentPath = get_current_path(request.path)

        menuItemObjList = [child for menuItemObj in menuItemList for child in menuItemObj['child'] if
                        child['menuItemLink'] == currentPath]
        
        job_boards = getJobboards(user_data)

        if menuItemObjList:
            return render(request, "portal_index.html", {"template_name": "job_boards.html", 'menuItemList': menuItemList,"job_boards":job_boards})
        else:
            return redirect('../')

    except Exception as e:
        raise


def overallDashboardPage(request):
    try:

        user_mail = request.user
        user_data = auth_user(user_mail)

        user_role = user_data.role

        menuItemList = get_functions_service(user_role)
        currentPath = get_current_path(request.path)

        company_id = getCompanyId(request.user)
        
        dashboard_data = getDashboardData(company_id)
        dashboard_counts = getOverallDashboardCounts(company_id)
        # print("dashboard_counts",dashboard_counts)

        menuItemObjList = [child for menuItemObj in menuItemList for child in menuItemObj['child'] if
                        child['menuItemLink'] == currentPath]

        if menuItemObjList:
            return render(request, "portal_index.html", {"template_name": "overall_dashboard.html", 'menuItemList': menuItemList,'dashboard_data':dashboard_data,"dashboard_counts":dashboard_counts })
    
        else:
            return redirect('../')

    except Exception as e:
        raise
    
    
    
def source_performance_reportPage(request):
    if not request.user.is_active and not request.user.is_staff:
        return user_not_active(request, after_login_redirect_to=str(request.META["PATH_INFO"]))
    
    try:

        user_mail = request.user
        user_data = auth_user(user_mail)

        user_role = user_data.role

        menuItemList = get_functions_service(user_role)
        
        payload={"cid":user_data.companyid}
        source_performance = SourcePerformanceService(payload)


        
        return render(request, "portal_index.html", {"template_name": 'source_performance_report.html','menuItemList':menuItemList,
                                                                     "recruiter_report": source_performance["data"], "from_date": source_performance["from_date"], "to_date": source_performance["to_date"],
                                                                     })
    
    except Exception as e:
        raise


def resumeTemplatesPage(request):
    try:

        user_mail = request.user
        user_data = auth_user(user_mail)

        user_role = user_data.role

        menuItemList = get_functions_service(user_role)

        company_id = getCompanyId(request.user)

        resume_templates = getResumeTemplates(company_id)

        return render(request, "portal_index.html", {"template_name": "branded_templates.html", 'menuItemList': menuItemList,"resume_templates":resume_templates })
    
    except Exception as e:
        raise