import ast
import os
from datetime import datetime
import json
import logging
import time
import threading
import re
import base64
from urllib.parse import urljoin

import requests
from django.http import JsonResponse, FileResponse
from app_api.functions.enc_dec import decrypt_code, encrypt_code
from hirelines.settings import BASE_DIR
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from django.http import HttpResponse, JsonResponse, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt
from allauth.account.utils import perform_login
from allauth.account import app_settings as allauth_settings
from app_api.functions.masterdata import auth_user, getCompanyId, getUserCompany
from django.db.models import Q

from hirelines.metadata import getConfig, check_referrer
from .functions.services import addCompanyDataService, candidateRegistrationService, deductCreditsService, registerUserService, authentication_service, getJdWorkflowService,interviewSchedulingService, jdPublishService, changeUserstatusService, updateJdDataService, skillsWithTopicsWithSubtopicsWithQuestionsService, \
        jdTestAdd, addJdServices, updateJdServices, workFlowDataService, interviewCompletionService,questionsResponseService, getInterviewStatusService, generateCandidateReport, addNewUserService, \
        notifyCandidateService,checkTestHasPaperService, deleteTestInJdService, saveInterviewersService,generateCandidateReport,demoUserService, updateCandidateWorkflowService, dashBoardGraphDataService,mapUploadedCandidateFields, processAddCandidateService, checkJdCandidateRegistrationService, \
        downloadUploadReportService, getResumeData, softDeleteResume, generateBrandedProfile,getRecritmentDashboardData, getJdProfileData, shortlistProfileService, dashBoardDataService, addNewClientService, changeClientstatusService,RecruitersPerformanceService, jobBoardConfigService
        
from .models import Account, Branding, Candidate, CompanyCredits, JobDesc, Lookupmaster, Registration, User, User_data, Workflow, InterviewMedia, CallSchedule,Brules,Profile,ProfileExperience,Source,ProfileSkills,Email_template, Company, ResumeFile, Resume, ProfileActivity, WorkCal,jdlibrary
# from .functions.database import addCandidateDB, scheduleInterviewDB, interviewResponseDB, addInterviewFeedbackDB, updateEmailtempDB, interviewRemarkSaveDB, updateCompanyDB, 
from .functions.database import addCandidateDB, scheduleInterviewDB, interviewResponseDB, addInterviewFeedbackDB, updateEmailtempDB, interviewRemarkSaveDB, updateCompanyDB, saveStarQuestion, demoRequestDB, deleteCandidateDB, updateSourcesDataDB, \
    updateCandidateInfoDB, updateDashboardDisplayFlagDB, addProfileDB, addResumeProfileDB, updateProfileDetailsDB, updateProfileEducationDB, updateProfileExperienceDB, updateProfileProjectsDB, updateProfileAwardsDB, updateProfileCertificatesDB, \
    updateProfileSkillsDB,updateProfileActivityDB,saveWorkCalDB,scheduleCandidateInterviewLinkDB,scheduleCandidateInterviewDB, jdRecruiterAssignDB,updateFullProfileDB, addWorkspaceDB, addProfileActivityDB,updateWorkspaceDB,updateProfileCompletion, \
    saveJobBoardConfigDB, saveJDJobBoardsDB, addResumeDB
from app_api.functions.constants import hirelines_registration_script, const_profile_status
from app_api.functions.email_resume import fetch_gmail_attachments

from app_api.functions.enc_dec import encrypt_code
# Create your views here.
from .functions.doc2pdf import convert_word_binary_to_pdf

@csrf_exempt
@api_view(['POST'])
@authentication_classes([])
@permission_classes([])
def addCompanyData(request):
    response = {
        'data':None,
        'error': None,
        'statusCode':11
    }
    try:
        if request.method == 'POST':
            dataObjs = json.loads(request.POST.get('data'))
            data_add_status = addCompanyDataService(dataObjs)
            response['statusCode'] = int(data_add_status)
    except Exception as e:
        response['data'] = 'Error in adding company data'
        response['error'] = str(e)
    return JsonResponse(response)


@csrf_exempt
@api_view(['POST'])
@authentication_classes([])
@permission_classes([])
def addJDCandidate(request):
    response = {
        'data': None,
        'error': None,
        'statusCode': 1
    }
    try:
        if request.method == "POST":
            dataObjs = json.loads(request.body)
            candidateRegistrationService(dataObjs)
            response['data'] = "Details Saved Sucessfully"
            response['statusCode'] = 0
    except Exception as e:
        response['data'] = 'Error in Registration'
        response['error'] = str(e)
        raise
    return JsonResponse(response)


@csrf_exempt
@api_view(['POST'])
@authentication_classes([])
@permission_classes([])
def registerUser(request):
    response = {
        'data':None,
        'error': None,
        'statusCode':11
    }
    try:
        if request.method == 'POST':
            dataObjs = json.loads(request.POST.get('data'))
            data_add_status = registerUserService(dataObjs)
            response['statusCode'] = int(data_add_status)
    except Exception as e:
        response['data'] = 'Error in adding company data'
        response['error'] = str(e)
        raise
    return JsonResponse(response)


@csrf_exempt
@api_view(['POST'])
@authentication_classes([])
@permission_classes([])
def loginUser(request):
    response = {
        'data':None,
        'error':None,
        'statusCode':1
    }
    try:
        if request.method == "POST":
            dataObjs = json.loads(request.POST.get('data'))
            auth_token = authentication_service(dataObjs)
           
            if auth_token[0] != None:
                usr = User_data.objects.filter(usr_email=dataObjs['email']).first()
                perform_login(request._request, usr, allauth_settings.EMAIL_VERIFICATION, signup=False,
                              redirect_url=None, signal_kwargs=None)
                user = auth_user(usr)
                response['token'] = 'token_generated'
                response['data'] = user.role
                response['login_type'] = auth_token[1]
            else:
                response['token'] = 'AnonymousUser'
                response['data'] = 'login failed'
            response['statusCode'] = 0
    except Exception as e:
        response['data'] = 'Error in Sign-in'
        response['error'] = str(e)
        raise
    return JsonResponse(response)


@api_view(['POST'])
def addCompanyData(request):
    response = {
        'data':None,
        'error': None,
        'statusCode':11
    }
    try:
        if request.method == 'POST':
            dataObjs = json.loads(request.POST.get('data'))
            data_add_status = addCompanyDataService(dataObjs)
            response['statusCode'] = int(data_add_status)
    except Exception as e:
        response['data'] = 'Error in adding company data'
        response['error'] = str(e)
        raise
    return JsonResponse(response)


@api_view(['POST'])
def jdAddTest(request):
    response = {
        'data':None,
        'error': None,
        'statusCode':1
    }
    try:
        if request.method == 'POST':
            dataObjs = json.loads(request.POST.get('data'))
            companyID = getCompanyId(request.user)
            testData = jdTestAdd(dataObjs,companyID)
            response['data'] = testData
            response['statusCode'] = 0
    except Exception as e:
        response['data'] = 'Error in adding Test in Work flow'
        response['error'] = str(e)
        raise
    return JsonResponse(response)


@api_view(['POST'])
def addJD(request):
    response = {
        'data':None,
        'error': None,
        'statusCode':1
    }
    try:
        if request.method == 'POST':
            dataObjs = json.loads(request.POST.get('data'))
            companyID = getCompanyId(request.user)
            jdData = addJdServices(dataObjs,companyID,request.user)
            response['data'] = jdData
            response['statusCode'] = 0
    except Exception as e:
        response['data'] = 'Error in Saving JD Data'
        response['error'] = str(e)
        raise
    return JsonResponse(response)


@api_view(['POST'])
def jdUpdateData(request):
    response = {
        'data':None,
        'error': None,
        'statusCode':1
    }
    try:
        if request.method == 'POST':
            dataObjs = json.loads(request.POST.get('data'))
            companyID = getCompanyId(request.user)
            jdDataDict = updateJdDataService(dataObjs)
            response['data'] = jdDataDict
            response['statusCode'] = 0
    except Exception as e:
        response['data'] = 'Error in getting JD data'
        response['error'] = str(e)
        raise
    return JsonResponse(response)


@api_view(['POST'])
def updateJD(request):
    response = {
        'data':None,
        'error': None,
        'statusCode':1
    }
    try:
        if request.method == 'POST':
            dataObjs = json.loads(request.POST.get('data'))
            companyID = getCompanyId(request.user)
            updateJdServices(dataObjs,companyID,request.user)
            response['statusCode'] = 0
    except Exception as e:
        response['data'] = 'Error in JD Updata data'
        response['error'] = str(e)
        raise
    return JsonResponse(response)


@api_view(['GET'])
def getJdWorkflow(request):
    response = {
        'data':None,
        'error':None,
        'statusCode':1
    }
    try:
        if request.method == "GET":
            jobid = request.GET.get('jid')
            company_id = getCompanyId(request.user)
            workflow_data = getJdWorkflowService(jobid,company_id)
            response['data'] = workflow_data
            response['statusCode'] = 0

    except Exception as e:
        response['data'] = 'Error in getting jd worflow'
        response['error'] = str(e)
        raise
    return JsonResponse(response)


@api_view(['GET','POST'])
def getJdQuestionsView(request):
    response = {
        'data': None,
        'error': None,
        'statusCode': 1
    }
    try:
        if request.method == "POST":
            user = auth_user(request.user)
            user_company = user.companyid
            # enc_company_id = encrypt_code(user_company)
            
            acert_domain = getConfig()['DOMAIN']['acert']
            endpoint = '/api/jd-screening-questions'
            url = urljoin(acert_domain, endpoint)
            dataObjs = json.loads(request.POST.get('data'))

            # print("getJdQuestionsView dataObjs",dataObjs)
            jd_data = JobDesc.objects.filter(id=dataObjs["jd_id"],companyid=user_company).values("skillset","location","expmin","expmax").last()
            
            skills_list=[]
            skill_set = ast.literal_eval(jd_data["skillset"])
            for skill in skill_set:
                skill = ", ".join(skill.keys())
                skills_list.append(skill)
            jd_data['skillset'] = skills_list

            screeningPaper = ""
            workFlowData = Workflow.objects.filter(jobid = dataObjs["jd_id"])
            if workFlowData:
                for workFlow_ in workFlowData:
                    if workFlow_:
                        if workFlow_.id == dataObjs["test_id"] and workFlow_.papertype == "S":
                            if workFlow_.paperid:
                                screeningPaper = workFlow_.paperid
            if jd_data:
                jd_data['screeningPaper'] = screeningPaper

            jd_data['test_id'] = dataObjs['test_id']
            jd_data['company_id'] = user_company
            print('jd_data',jd_data)
            get_evaluation_submissions = requests.post(url, json = jd_data, verify = False)
            response_content = get_evaluation_submissions.content

            if response_content:
                
                json_data = json.loads(response_content.decode('utf-8'))

                acert_data = json_data['data']

                jd_questions = acert_data
                if json_data['statusCode'] == 0:
                    response['data'] = jd_questions
                    response['statusCode'] = 0
            
    except Exception as e:
        response['data'] = 'Error in getJdQuestionsView'
        response['error'] = str(e)
        print(str(e))
        # raise
        # logging.error("Error in getJdQuestionsView : ", str(e))
    return JsonResponse(response)


@api_view(['POST'])
def addCandidate(request):
    response = {
        'data': None,
        'error': None,
        'statusCode': 1
    }
    try:
        if request.method == "POST":
            dataObjs = json.loads(request.POST.get('data'))
            user_email = request.user
            user = auth_user(request.user)
            company_id = getCompanyId(user_email)

            c_data = addCandidateDB(dataObjs,company_id,None,user.id)
            response['data'] = c_data
            response['statusCode'] = 0
        else:
            return HttpResponseForbidden('Request Blocked')
       
    except Exception as e:
        response['data'] = 'Error in saving Job Description'
        response['error'] = str(e)
        raise

    return JsonResponse(response)


# @api_view(['POST'])
# def workFlowData(request):
#     response = {
#         'data': None,
#         'error': None,
#         'statusCode': 1
#     }
#     try:
#         if request.method == "POST":
#             dataObjs = json.loads(request.POST.get('data'))
#             user_email = request.user
#             company_id = getCompanyId(user_email)
#             workflowData = workFlowDataService(dataObjs,company_id)
#             response['data'] = workflowData
#             response['statusCode'] = 0
#         else:
#             return HttpResponseForbidden('Request Blocked')
       
#     except Exception as e:
#         response['data'] = 'Error in saving Job Description'
#         response['error'] = str(e)
#         raise

#     return JsonResponse(response)

@api_view(['POST'])
def workFlowData(request):
    response = {
        'data': None,
        'error': None,
        'statusCode': 1
    }
    try:
        if request.method == "POST":
            dataObjs = json.loads(request.POST.get('data'))
            user_email = request.user
            company_id = getCompanyId(user_email)
            workflowData = workFlowDataService(dataObjs,company_id)
            response['data'] = workflowData
            response['statusCode'] = 0
        else:
            return HttpResponseForbidden('Request Blocked')
       
    except Exception as e:
        response['data'] = 'Error in saving Job Description'
        response['error'] = str(e)
        raise

    return JsonResponse(response)


@api_view(['GET'])
def interviewScheduling(request,cid):

    response = {
        'data': None,
        'error': None,
        'statusCode': 1
    }
    try:

        user = auth_user(request.user)
        if request.method == "GET":
            int_id = request.GET.get('int_id')
            interview_schedule_data = interviewSchedulingService(cid,int_id)
            response['data'] = interview_schedule_data
            response['statusCode'] = 0

    except Exception as e:
        response['data'] = 'Error in Call Scheduling view'
        response['error'] = str(e)
        raise
    return JsonResponse(response)



@api_view(['POST'])
def scheduleInterviewView(request):
    response = {
        'data': None,
        'error': None,
        'statusCode': 1
    }
    try:
        if request.method == "POST":
            user = auth_user(request.user)
            dataObjs = json.loads(request.POST.get('data'))
            res = scheduleInterviewDB(user.id, dataObjs)
            response['data'] = res
            response['statusCode'] = 0

    except Exception as e:
        response['data'] = 'Error in Scheduling Interview view'
        response['error'] = str(e)
    return JsonResponse(response) 




def candidateRegistrationCDNForm(request,enc_jdid):
    
    try:
        # Restrict other company domains, commented due to testing.
        
        # request_domain = request.META.get('HTTP_HOST', '')
        # print("request_domain",request_domain)
        # # enccode = encrypt_code(52)
        # # print("enccode",enccode)
        # if "local" in request_domain:
        #     print("domain identified")
        # deccode =  decrypt_code(enc_jdid)
        # print("deccode",deccode)
        
        # hirelines_registration_script Reads registration cdn script from constants
        return HttpResponse(hirelines_registration_script, content_type='application/javascript')
    except:
        return HttpResponse('console.error("Script not found");', content_type='application/javascript')



@api_view(['POST'])
def interviewResponseView(request):
    response = {
        'data': None,
        'error': None,
        'statusCode': 1
    }
    try:

        if request.method == "POST":

            dataObjs = json.loads(request.POST.get('data'))

            res = interviewResponseDB(dataObjs)

            response['data'] = res
            response['statusCode'] = 0

    except Exception as e:
        response['data'] = 'Error in Meeting Response view'
        response['error'] = str(e)
    return JsonResponse(response)


@api_view(['POST'])
def questionsResponseView(request):
    response = {
        'data': None,
        'error': None,
        'statusCode': 1
    }

    try:
        if request.method == "POST":
            dataObjs = json.loads(request.POST.get('data'))

            res = questionsResponseService(dataObjs)

            response['data'] = res
            response['statusCode'] = 0

    except Exception as e:
        response['data'] = 'Error in questios Response view'
        response['error'] = str(e)

    return JsonResponse(response)


@csrf_exempt
@api_view(['POST'])
@authentication_classes([])
@permission_classes([])
def registerCandidate(request):
    response = {
        'data': None,
        'error': None,
        'statusCode': 1
    }
    try:
        if request.method == "POST":
            dataObjs = json.loads(request.body)
            #decrypt encjdid
            jd_id = decrypt_code(dataObjs["encjdid"])
            job_description = JobDesc.objects.get(id=jd_id)
            app_config = getConfig()['APP_CONFIG']
            register_candidate_once_per_jd = app_config["register_candidate_once_per_jd"]
            if register_candidate_once_per_jd == "Y":
                check_candidate_registered = "Y"
            # if register_candidate_once_per_jd == "N":
            #     check_candidate_registered = "N"                
            else:
                check_candidate_registered = Candidate.objects.filter(companyid = job_description.companyid,
                    jobid = job_description.id,
                    email = dataObjs["email"])

            # if (not check_candidate_registered) or (check_candidate_registered == "Y"):
            if (not check_candidate_registered) or (check_candidate_registered == "N"):
                if job_description.status == "A":
                    workflow_data = Workflow.objects.filter(jobid=jd_id,order=1).last()
                    if workflow_data:
                        company_id = workflow_data.companyid
                        dataObjs["jd"] = jd_id
                        dataObjs['begin-from'] = workflow_data.paperid
                        company_id = workflow_data.companyid
                        add_resp  =  addCandidateDB(dataObjs,company_id,workflow_data)
                        if add_resp == "insufficient_credits":
                            response['data'] = 'Insufficient Credits'
                        else:
                            response['data'] = 'Registration completed successfully'
                    else:
                        response['data'] = 'Workflow not defined'
                else:
                    response['data'] = 'JD inactive'
            else:
                response['data'] = 'Candidate already registered'
            response['statusCode'] = 0
    except Exception as err:
        response['data'] = 'Error in registerCandidate'
        response['error'] = str(err)
        raise
    return JsonResponse(response)


@api_view(['GET','POST'])
def evaluationView(request):
    response = {
        'data': None,
        'error': None,
        'statusCode': 1
    }
    try:
        if request.method == "GET":# and check_referrer(request):
            # company_id = request.GET.get('cid', 0)
            # print("company_id",company_id)
            user = auth_user(request.user)
            user_company = user.companyid
            enc_company_id = encrypt_code(user_company)
            
            acert_domain = getConfig()['DOMAIN']['acert']
            endpoint = '/api/evaluate-papers'
            url = urljoin(acert_domain, endpoint)

            company_paper_ids = list(Workflow.objects.filter(companyid=user_company).values_list("paperid",flat=True))
            company_papers={
                "request_for":"get_evaluation_papers",
                "enc_company_id":enc_company_id,
                "company_paper_ids":company_paper_ids
                } 
            get_evaluation_papers = requests.post(url,json=company_papers, verify=False)
            
            response_content = get_evaluation_papers.content
            # print("response_content",response_content)
            if response_content:
                
                json_data = json.loads(response_content.decode('utf-8'))

                acert_data = json_data['data']
                if json_data['statusCode'] == 0:
                    response['data'] = acert_data
                    response['statusCode'] = 0

        if request.method == "POST":
            user = auth_user(request.user)
            user_company = user.companyid
            enc_company_id = encrypt_code(user_company)
            
            acert_domain = getConfig()['DOMAIN']['acert']
            endpoint = '/api/evaluate-papers'
            url = urljoin(acert_domain, endpoint)

            
            company_paper_ids = list(Workflow.objects.filter(companyid=user_company).values_list("paperid",flat=True))
            
            dataObjs = json.loads(request.POST.get('data'))
           
            if dataObjs["request_for"] == "submissions":

                dataObjs["enc_company_id"]=enc_company_id
                dataObjs["company_paper_ids"]=company_paper_ids
                
                get_evaluation_submissions = requests.post(url, json = dataObjs, verify = False)
                response_content = get_evaluation_submissions.content

                if response_content:
                    
                    json_data = json.loads(response_content.decode('utf-8'))

                    acert_data = json_data['data']
                    evaluationquestions = acert_data
                    if json_data['statusCode'] == 0:
                        response['data'] = evaluationquestions
                        response['statusCode'] = 0
            
            if dataObjs["request_for"] == "update_marks":
                
                dataObjs["enc_company_id"]=enc_company_id
                dataObjs["company_paper_ids"]=company_paper_ids
                
                update_marks = requests.post(url, json = dataObjs, verify = False)
                response_content = update_marks.content

                if response_content:
                    
                    json_data = json.loads(response_content.decode('utf-8'))

                    acert_data = json_data['data']
                    answer_data = json_data["answer_data"]
                    response['data'] = "Marks Updated successfully"
                    if json_data['statusCode'] == 0:
                        response['answer_data'] = answer_data
                        response['statusCode'] = 0
            
            if dataObjs["request_for"] == "send_evaluation_result":

                
                dataObjs["enc_company_id"]=enc_company_id
                dataObjs["company_paper_ids"]=company_paper_ids

                if dataObjs["paper_id"] in company_paper_ids:
                    update_marks = requests.post(url, json = dataObjs, verify = False)
                    response_content = update_marks.content

                    if response_content:
                        
                        resp = json.loads(response_content.decode('utf-8'))
                        
                        acert_data = resp['data']
                        if resp["statusCode"] == 0:
                            response['data'] = acert_data
                            response['statusCode'] = 0
                else:                
                    response['data'] = "Query Not Found"
                    response['statusCode'] = 0

        
    except Exception as e:
        response['data'] = 'Error in evaluationquestionsView'
        response['error'] = str(e)
        print(str(e))
        # raise
        # logging.error("Error in evaluationquestionsView : ", str(e))
    return JsonResponse(response)



@api_view(['POST'])
@authentication_classes([])
@permission_classes([])
def getInterviewStatusView(request):
    response = {
        'data': None,
        'error': None,
        'statusCode': 1
    }
    try:
        if request.method == "POST":            
            dataObjs = json.loads(request.POST.get('data'))
            res = getInterviewStatusService(dataObjs)
            response['data'] = res
            response['statusCode'] = 0

    except Exception as e:
        response['data'] = 'Error in getCallStatus'
        response['error'] = str(e)
    return JsonResponse(response)


@api_view(['GET', 'POST'])
@authentication_classes([])
@permission_classes([])
def interviewFile(request):

    dataObjs = json.loads(request.POST.get('data'))

    c_code = str(dataObjs["reg_code"]).split("_")[1]
    schid = str(dataObjs["reg_code"]).split("_")[2].split(".")[0]

    candidate_details = Candidate.objects.filter(candidateid=c_code).last()
    
    InterviewMedia(recorded=dataObjs["videoid"], candidateid=candidate_details.id).save()

    call_details = CallSchedule.objects.filter(id=schid).last()
    call_details.callendflag = 'Y'
    call_details.save()

    return JsonResponse({"response": "success"})


@api_view(['POST'])
def interviewCompletion(request):
    response = {
        'data': None,
        'error': None,
        'statusCode': 1
    }
    try:
        if request.method == "POST":
            dataObjs = json.loads(request.POST.get('data'))

            user = auth_user(request.user)

            interviewCompletionService(dataObjs,user.id)

            response['data'] = "Saved"
            response['statusCode'] = 0

    except Exception as e:
        response['data'] = 'Error in Saving Meeting Status view'
        response['error'] = str(e)
        
    return JsonResponse(response)


@api_view(['POST'])
def interviewFeedback(request):
    response = {
        'data': None,
        'error': None,
        'statusCode': 1
    }
    try:
        if request.method == "POST":
            user = auth_user(request.user)
            dataObjs = json.loads(request.POST.get('data'))
            addInterviewFeedbackDB(user, dataObjs)
            response['data'] = "Feedback given successfully"
            response['statusCode'] = 0

    except Exception as e:
        response['data'] = 'Error in feedback view'
        response['error'] = str(e)
    return JsonResponse(response)


@api_view(['POST'])
def deleteTestinJs(request):
    response = {
        'data': None,
        'error': None,
        'statusCode': 1
    }
    try:
        if request.method == "POST":
            user = auth_user(request.user)
            dataObjs = json.loads(request.POST.get('data'))
            testDetails = deleteTestInJdService(user, dataObjs)
            response['data'] = testDetails
            if testDetails['msg'] == 'Deleted-successfully':
                response['statusCode'] = 0

    except Exception as e:
        response['data'] = 'Error in Deleting Test from workflow'
        response['error'] = str(e)
        raise
    return JsonResponse(response)


@api_view(['POST'])
def saveInterviewersForJd(request):
    response = {
        'data': None,
        'error': None,
        'statusCode': 1
    }
    try:
        if request.method == "POST":
            user = auth_user(request.user)
            dataObjs = json.loads(request.POST.get('data'))
            interviwersData = saveInterviewersService(user, dataObjs)
            response['data'] = interviwersData
            response['statusCode'] = 0

    except Exception as e:
        response['data'] = 'Error in saving interviewers'
        response['error'] = str(e)
        raise
    return JsonResponse(response)


@api_view(['POST'])
def checkTestHasPaper(request):
    response = {
        'data': None,
        'error': None,
        'statusCode': 1
    }
    try:
        if request.method == "POST":
            user = auth_user(request.user)
            dataObjs = json.loads(request.POST.get('data'))
            testaaPaperDetails = checkTestHasPaperService(user, dataObjs)
            response['data'] = testaaPaperDetails
            response['statusCode'] = 0

    except Exception as e:
        response['data'] = 'Error in Test has paper id'
        response['error'] = str(e)
    return JsonResponse(response)


@api_view(['POST'])
def updateEmailtemp(request):
    response = {
        'data': None,
        'error': None,
        'statusCode': 1
    }
    try:
        if request.method == "POST":
            user = auth_user(request.user)
            dataObjs = json.loads(request.POST.get('data'))
            fileObjs = request.FILES
            updateEmailtempDB(user, dataObjs,fileObjs)
            response['data'] = "Email Template updated successfully"
            response['statusCode'] = 0

    except Exception as e:
        response['data'] = 'Error in updateEmailtemp'
        response['error'] = str(e)
    
    return JsonResponse(response)


@api_view(["GET"])
@authentication_classes([])
@permission_classes([])
def candidateReport(request):
    response = {"data": None, "error": None, "statusCode": 1}

    try:

        candidate_id = request.GET.get('cid')
        pdf_path = generateCandidateReport(candidate_id)
        
        with open(pdf_path['file_path'], 'rb') as pdf_file:
            response = HttpResponse(pdf_file.read(), content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="{pdf_path["file_name"]}.pdf"'

            return response
        
    except Exception as e:
        response["data"] = "Error in downloading report"
        response["error"] = str(e)

    return JsonResponse(response)


@api_view(['POST'])
def jdPublish(request):
    response = {
        'data': None,
        'error': None,
        'statusCode': 1
    }
    try:
        if request.method == "POST":
            user = auth_user(request.user)
            dataObjs = json.loads(request.POST.get('data'))
            companyData = getCompanyId(request.user)
            
            jdData = jdPublishService(dataObjs,companyData)

            response['data'] = jdData
            response['statusCode'] = 0

    except Exception as e:
        response['data'] = 'Error in Jd Publish'
        response['error'] = str(e)
        raise
    
    return JsonResponse(response)


@api_view(['POST'])
def notifyCandidate(request):
    response = {
        'data': None,
        'error': None,
        'statusCode': 1
    }
    try:
        if request.method == "POST":
            user = auth_user(request.user)
            dataObjs = json.loads(request.POST.get('data'))
            notifyCandidateService(dataObjs,user)
            response['data'] = "Candidate Notified Successfully"
            response['statusCode'] = 0

    except Exception as e:
        response['data'] = 'Error in Candidate Notify view'
        response['error'] = str(e)
    return JsonResponse(response)


@api_view(['POST'])
@authentication_classes([])
@permission_classes([])
def getUpdateCompanyCreditsView(request):
    response = {
        'data': None,
        'error': None,
        'statusCode': 1
    }
    try:
        if request.method == "POST":
            dataObjs = request.data
            company_id = decrypt_code(dataObjs["company_id"])
            if dataObjs["request_type"] == "check_credits":

                paper_type = dataObjs["paper_type"]
                company_account = Account.objects.get(companyid=company_id)
                company_credits = CompanyCredits.objects.get(companyid=company_id,transtype=paper_type)
                credit_availablity_stat = "N"

                if company_account.balance >= company_credits.credits:
                    credit_availablity_stat = "Y"
                    current_credits = company_account.balance-company_credits.credits
                else:
                    credit_availablity_stat = "N"
                    current_credits = company_account.balance
                
                    
                app_config = getConfig()['APP_CONFIG']
                lowcredits_warning = int(app_config["lowcredits_warning"])
                reg_stop_warning = int(app_config["reg_stop_warning"])
                if current_credits<=reg_stop_warning:
                    credits_status =  "N"
                elif current_credits<=lowcredits_warning:
                    credits_status = "L"
                else:
                    credits_status = "A"
                send_lowcredits_notification = "N"
                if (credits_status ==  "N") or (credits_status == "L"):
                    if company_account.lowcreditsnotification != "Y":
                        send_lowcredits_notification = "Y"
                        company_account.lowcreditsnotification = "Y"
                        company_account.save()

                hr_admin_label = "HR-Admin"
                hradmin_emails_list = list(User.objects.filter(companyid=company_id,role__contains=hr_admin_label,status="A").values_list("email",flat=True))
                
                response["data"]={
                    "company_id":company_id,
                    "credit_availablity_stat":credit_availablity_stat,
                    "credits_status":credits_status,
                    "hradmin_emails_list":hradmin_emails_list,
                    "current_credits":current_credits,
                    "send_lowcredits_notification":send_lowcredits_notification
                }
                
            if dataObjs["request_type"] == "deduct_credits":
                paper_type = dataObjs["paper_type"]
                paper_id = dataObjs["paper_id"]
                deductCreditsService(company_id,paper_type,paper_id)
            response['statusCode'] = 0

    except Exception as e:
        response['data'] = 'Error in getUpdateCompanyCreditsView'
        response['error'] = str(e)
        # raise
    return JsonResponse(response)



@api_view(['GET'])
def getCreditsView(request):
    response = {
        'data': None,
        'error': None,
        'statusCode': 1
    }
    try:
        if request.method == "GET":
            user = auth_user(request.user)
            user_company = user.companyid
            company_account = Account.objects.get(companyid=user_company)
            app_config = getConfig()['APP_CONFIG']
            lowcredits_warning = int(app_config["lowcredits_warning"])
            reg_stop_warning = int(app_config["reg_stop_warning"])
            if company_account.balance<=reg_stop_warning:
                credits_avaliabilty =  "N"
            elif company_account.balance<=lowcredits_warning:
                credits_avaliabilty = "L"
            else:
                credits_avaliabilty = "A"
                
            company_account_obj = {
                "balance_credits":company_account.balance,
                "credits_avaliabilty":credits_avaliabilty
            }
            response["data"] = company_account_obj
            response['statusCode'] = 0

    except Exception as e:
        response['data'] = 'Error in getCreditsView'
        response['error'] = str(e)
        # raise
    return JsonResponse(response)


@api_view(['GET','POST'])
def updateCompanyBrandingView(request):
    response = {
        'data': None,
        'error': None,
        'statusCode': 1
    }
    try:
        
        if request.method == "POST":
            user = auth_user(request.user)
            user_company = user.companyid
            enc_company_id = encrypt_code(user_company)
            dataObjs = json.loads(request.POST.get('data'))
            if dataObjs["request_type"] == "update_branding":
                fileObjs = request.FILES
                company_branding , company_branding_flag  = Branding.objects.get_or_create(companyid=user_company)
                company_branding.content=dataObjs['css_content']
                # company_branding.sociallinks=dataObjs['social_links']
                company_branding.status = dataObjs['status']
                company_branding.save()
                logo_file_path = ""
                logo_file = ""
                for file in fileObjs.items():
                    company_branding.logourl = file[1]
                    company_branding.save()
                    logo_file_path = str(company_branding.logourl)
                    logo_fullpath = f"{request.scheme}://{request.META['HTTP_HOST']}/media/{company_branding.logourl}"
                    company_branding.logourl = logo_fullpath
                    company_branding.save()
                    logo_file_path = BASE_DIR+"/media/"+logo_file_path
                    logo_file = {"logo":open(logo_file_path, 'rb')}
                dataObjs["cid"] = enc_company_id
                
                acert_domain = getConfig()['DOMAIN']['acert']
                endpoint = '/api/company-branding'
                url = urljoin(acert_domain, endpoint)
                
                update_response = requests.post(url, data = dataObjs,files=logo_file, verify = False)

                response_content = update_response.content

                if response_content:
                    json_data = json.loads(response_content.decode('utf-8'))
                    resp_status_code = json_data['statusCode']
                    if resp_status_code == 0:
                        response['data'] = "Branding updated successfully"
                        response['statusCode'] = 0
                        
    except Exception as e:
        response['data'] = 'Error in updateCompanyBrandingView'
        response['error'] = str(e)
        # raise
        logging.error("Error in updateCompanyBrandingView : ", str(e))
    return JsonResponse(response)


def getUserName(request):
    user = auth_user(request.user)
    company = getUserCompany(user.companyid)
    return JsonResponse({"name": user.name,"companyname":company.name})


@api_view(['POST'])
def addNewUsers(request):
    response = {
        'data': None,
        'error': None,
        'statusCode': 1
    }
    try:
        user = auth_user(request.user)
        dataObjs = dataObjs = json.loads(request.POST.get('data'))
        userData = addNewUserService(user.companyid,dataObjs)
        response['data'] = userData
        response['statusCode'] = 0

    except Exception as e:
        response['data'] = 'Error in Creating New User'
        response['error'] = str(e)
        raise
    return JsonResponse(response)


@api_view(['POST'])
def changeUserStatus(request):
    response = {
        'data': None,
        'error': None,
        'statusCode': 1
    }
    try:
        user = auth_user(request.user)
        dataObjs = dataObjs = json.loads(request.POST.get('data'))
        userData = changeUserstatusService(user.companyid,dataObjs)
        response['data'] = userData
        response['statusCode'] = 0

    except Exception as e:
        response['data'] = 'Error in Creating New User'
        response['error'] = str(e)
        raise
    return JsonResponse(response)


@api_view(['POST'])
@authentication_classes([])
@permission_classes([])
def updateHirelinesData(request):
    response = {
        'data': None,
        'error': None,
        'statusCode': 1
    }
    try:
        if request.method == "POST":
            dataObjs = request.data
            company_id = decrypt_code(dataObjs["company_id"])
            if dataObjs["update_type"] == "reg_status":
                candidate = Candidate.objects.get(candidateid=decrypt_code(dataObjs["participant_refid"]),
                                                 companyid=company_id)
                registration = Registration.objects.filter(companyid=company_id,
                                                           candidateid=candidate.id,
                                                           jobid=candidate.jobid,
                                                           papertype=dataObjs["paper_type"],
                                                           paperid=decrypt_code(dataObjs["paper_id"])).last()
                registration.completiondate = datetime.now()
                registration.status = dataObjs["update_value"]
                registration.save()
                
                response['data'] = "Registration status updated successfully"
                response['statusCode'] = 0
                
            if dataObjs["update_type"] == "candidate_status":
                candidate = Candidate.objects.get(candidateid=decrypt_code(dataObjs["participant_refid"]),
                                                 companyid=company_id)
                candidate.status = dataObjs["update_value"]
                candidate.save()
                response['data'] = "candidate status updated successfully"
                response['statusCode'] = 0
            
            if dataObjs["update_type"] == "add_registration":
                
                candidate = Candidate.objects.get(candidateid=decrypt_code(dataObjs["participant_refid"]),
                                                 companyid=company_id)
                
                paper_id = decrypt_code(dataObjs["paper_id"])
                
                registration = Registration(companyid=company_id,
                                                           candidateid=candidate.id,
                                                           jobid=candidate.jobid,
                                                           papertype=dataObjs["paper_type"],
                                                           paperid=paper_id,
                                                           registrationdate=datetime.now(),
                                                           status="I")
                registration.save()
                
                if dataObjs["paper_type"] == 'I':
                    job_desc = JobDesc.objects.get(id=candidate.jobid)
                    call_schedule = CallSchedule(
                        candidateid = candidate.id,
                        hrid = job_desc.createdby,
                        paper_id = paper_id,
                        status = 'N',
                        companyid = candidate.companyid
                    )
                    
                    call_schedule.save()

                if candidate.profileid:
                    if dataObjs["paper_type"] == "S":
                        addProfileActivityDB(candidate.profileid,"SC","Screening Sent")
                    elif dataObjs["paper_type"] == "E":
                        addProfileActivityDB(candidate.profileid,"CT","Coding Test Sent")

                response['data'] = "Registered successfully"
                response['statusCode'] = 0

    except Exception as e:
        response['data'] = 'Error in getUpdateCompanyCreditsView'
        response['error'] = str(e)
        raise
    return JsonResponse(response)


@api_view(['POST'])
def interviewRemarkSave(request):
    response = {
        'data': None,
        'error': None,
        'statusCode': 1
    }
    try:
        if request.method == "POST":
            dataObjs = json.loads(request.POST.get('data'))

            res = interviewRemarkSaveDB(dataObjs)

            response['data'] = res
            response['statusCode'] = 0

    except Exception as e:
        response['data'] = 'Error in save interview remark view'
        response['error'] = str(e)
    return JsonResponse(response)


@api_view(['POST'])
@authentication_classes([])
@permission_classes([])
def getJDData(request):

    response = {
        'data': None,
        'error': None,
        'statusCode': 1
    }
    try:
        if request.method == "POST":
            dataObjs = request.data
            
            company_id = decrypt_code(dataObjs["company_id"])
            cand_refid = dataObjs["cand_refid"]
            candidate = Candidate.objects.get(candidateid=cand_refid,companyid=company_id)
            jd_data = JobDesc.objects.filter(id=candidate.jobid).values().last()
            response['data'] = jd_data
            response['statusCode'] = 0

    except Exception as e:
        response['data'] = 'Error in getJDData'
        response['error'] = str(e)
    return JsonResponse(response)


@api_view(['POST'])
def makeAstarQuestion(request):
    response = {
        'data': None,
        'error': None,
        'statusCode': 1
    }
    try:
        if request.method == "POST":
            dataObjs = json.loads(request.POST.get('data'))
            saveStarQuestion(dataObjs)
            response['data'] = "make a star question"
            response['statusCode'] = 0

    except Exception as e:
        response['data'] = 'Error in update emails'
        response['error'] = str(e)
    
    return JsonResponse(response)


@api_view(['POST'])
def skillsWithTopicwithSubtopics(request):
    response = {
        'data': None,
        'error': None,
        'statusCode': 1
    }
    try:
        if request.method == "POST":
            dataObjs = json.loads(request.POST.get('data'))
            skillsData = skillsWithTopicsWithSubtopicsWithQuestionsService(dataObjs)
            response['data'] = skillsData
            response['statusCode'] = 0

    except Exception as e:
        response['data'] = "error while getting the topics for skills"
        response['error'] = str(e)
    
    return JsonResponse(response)


@api_view(['POST'])
def updateCompany(request):
    response = {
        'data': None,
        'error': None,
        'statusCode': 1
    }
    try:
        if request.method == "POST":
            dataObjs = json.loads(request.POST.get('data'))
            updateCompanyDB(dataObjs)
            response['data'] = "Company details updated successfully"
            response['statusCode'] = 0

    except Exception as e:
        response['data'] = 'Error in update emails'
        response['error'] = str(e)
    
    return JsonResponse(response)



@csrf_exempt
@api_view(['POST'])
@authentication_classes([])
@permission_classes([])
def demoUser(request):
    response = {
        'data':None,
        'error': None,
        'statusCode':1
    }
    try:
        if request.method == 'POST':
            dataObjs = json.loads(request.POST.get('data'))
            demo_id = demoUserService(dataObjs)
            response['data'] = demo_id
            response['statusCode'] = 0
    except Exception as e:
        response['data'] = 'Error in adding demo user'
        response['error'] = str(e)
    return JsonResponse(response)



@csrf_exempt
@api_view(['POST'])
@authentication_classes([])
@permission_classes([])
def demoRequest(request):
    response = {
        'data':None,
        'error': None,
        'statusCode':1
    }
    try:
        if request.method == 'POST':
            dataObjs = json.loads(request.POST.get('data'))
            demoRequestDB(dataObjs)
            response['data'] = "Demo requested"
            response['statusCode'] = 0
    except Exception as e:
        response['data'] = 'Error in requesting demo'
        response['error'] = str(e)
    return JsonResponse(response)


@api_view(['POST'])
def deleteCandidate(request):
    response = {
        'data': None,
        'error': None,
        'statusCode': 1
    }
    try:
        if request.method == "POST":
            dataObjs = json.loads(request.POST.get('data'))
            deleteCandidateDB(dataObjs)
            response['data'] = "Candidate deleted"
            response['statusCode'] = 0

    except Exception as e:
        response['data'] = 'Error in deleting the candidates'
        response['error'] = str(e)
    
    return JsonResponse(response)



@api_view(['POST'])
def updateCandidateWorkflow(request):
    response = {
        'data': None,
        'error': None,
        'statusCode': 1
    }
    try:
        if request.method == "POST":
            dataObjs = json.loads(request.POST.get('data'))
            updated_data = updateCandidateWorkflowService(dataObjs)
            response['data'] = int(updated_data)
            response['statusCode'] = 0

    except Exception as e:
        response['data'] = 'Error in updating candidate workflow data'
        response['error'] = str(e)
    
    return JsonResponse(response)



@api_view(['GET'])
def getDashboardGraphData(request):
    response = {
        'data': None,
        'error': None,
        'statusCode': 1
    }
    try:
        if request.method == "GET":
            company_id = getCompanyId(request.user)
            dashboard_data = dashBoardGraphDataService(company_id)
            response['data'] = dashboard_data
            response['statusCode'] = 0

    except Exception as e:
        response['data'] = 'Error in getting dashboard data'
        response['error'] = str(e)
    
    return JsonResponse(response)



@api_view(['POST'])
def updateSourceData(request):
    response = {
        'data': None,
        'error': None,
        'statusCode': 1
    }
    try:
        if request.method == "POST":
            company_id = getCompanyId(request.user)
            dataObjs = json.loads(request.POST.get('data'))
            updateSourcesDataDB(dataObjs,company_id)
            response['data'] = "Sources Data Updated"
            response['statusCode'] = 0

    except Exception as e:
        response['data'] = 'Error in getting dashboard data'
        response['error'] = str(e)
    
    return JsonResponse(response)


@api_view(['POST'])
def updateCandidateInfo(request):
    response = {
        'data': None,
        'error': None,
        'statusCode': 1
    }
    try:
        if request.method == "POST":
            company_id = getCompanyId(request.user)
            dataObjs = json.loads(request.POST.get('data'))
            updateCandidateInfoDB(dataObjs,company_id)
            response['data'] = "Candidate info Updated"
            response['statusCode'] = 0

    except Exception as e:
        response['data'] = 'Error in updating candidate info'
        response['error'] = str(e)
    
    return JsonResponse(response)



@api_view(['POST'])
def candidateUploadFile(request):
    response = {
        'data': None,
        'error': None,
        'statusCode': 1
    }
    try:
        if request.method == "POST":
            user = auth_user(request.user)
            company_id = getCompanyId(request.user)
            fileObjs = request.FILES
            mapping_response = mapUploadedCandidateFields(company_id,user.id,fileObjs)
            response['data'] = mapping_response
            response['statusCode'] = 0

    except Exception as e:
        response['data'] = 'Error in excel mapping response data'
        response['error'] = str(e)
        raise
    
    return JsonResponse(response)



@api_view(['POST'])
def confirmedCandidateData(request):
    response = {
        'data': None,
        'error': None,
        'statusCode': 1
    }
    try:
        if request.method == "POST":
            company_id = getCompanyId(request.user)
            dataObjs = json.loads(request.POST.get('data'))
            user = auth_user(request.user)
            thread = threading.Thread(target=processAddCandidateService, args=(company_id, dataObjs, user.id))
            thread.daemon = True
            thread.start()
            # data = confirmedCandidateDataService(dataObjs)
            # response['data'] = data
            response['statusCode'] = 0

    except Exception as e:
        response['data'] = 'Error in confirmed candidate data service'
        response['error'] = str(e)
        raise
    
    return JsonResponse(response)




@api_view(['POST'])
def updateDashboardDisplayFlag(request):
    response = {
        'data': None,
        'error': None,
        'statusCode': 1
    }
    try:
        if request.method == "POST":
            company_id = getCompanyId(request.user)
            dataObjs = json.loads(request.POST.get('data'))
            updateDashboardDisplayFlagDB(dataObjs,company_id)
            response['data'] = "Data Updated"
            response['statusCode'] = 0

    except Exception as e:
        response['data'] = 'Error in updating dashboard display data'
        response['error'] = str(e)
    
    return JsonResponse(response)



@api_view(['POST'])
def checkJdCandidateRegistration(request):
    response = {
        'data': None,
        'error': None,
        'statusCode': 1
    }
    try:
        if request.method == "POST":
            dataObjs = json.loads(request.POST.get('data'))
            registration_flag = checkJdCandidateRegistrationService(dataObjs)
            response['data'] = registration_flag
            response['statusCode'] = 0

    except Exception as e:
        response['data'] = 'Error in checking candidate registration data'
        response['error'] = str(e)
        raise
    
    return JsonResponse(response)


@api_view(['POST'])
def downloadUploadReport(request):
    response = {
        'data': None,
        'error': None,
        'statusCode': 1
    }
    try:
        if request.method == "POST":
            company_id = getCompanyId(request.user)
            report_file_data = downloadUploadReportService(company_id)

            response = FileResponse(
                open(report_file_data['report_file_path'], 'rb'),
                content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
            response["Content-Disposition"] = f"attachment; filename={report_file_data['report_file_name']}"
            return response

    except Exception as e:
        response['data'] = 'Error in downloading Upload Report'
        response['error'] = str(e)
        raise
    
    return JsonResponse(response)




@api_view(['GET'])
@authentication_classes([])  # no authentication
@permission_classes([])      # public access
def get_paperid(request):
    response = {'paper_id': None, 'error': None}
    try:
        test_id = request.GET.get('test_id')
        if not test_id:
            response['error'] = "Missing test_id"
            return JsonResponse(response, status=400)

        brule = Brules.objects.filter(workflowid=test_id).first()
        if brule:
            response['paper_id'] = brule.paperid
        else:
            response['error'] = f"No paper found for test_id {test_id}"
    except Exception as e:
        response['error'] = str(e)
    return JsonResponse(response)




def filter_profiles_api(request):

    data = json.loads(request.POST.get("data", "{}"))

    title = data.get("title", "")
    exp_from = data.get("exp_from", "")
    exp_to = data.get("exp_to", "")
    source_code = data.get("source", "")
    skills = data.get("skills", "")
    status = data.get("status", "")
    date_from = data.get("date_from", "")
    date_to = data.get("date_to", "")

    exp_from = int(exp_from) if exp_from else None
    exp_to = int(exp_to) if exp_to else None

  
    login_user = request.user

    company_id=User.objects.get(email=login_user).companyid 

    filtered_profiles = Profile.objects.filter(companyid=company_id).order_by("-dateofcreation")

    if title:
        filtered_profiles = filtered_profiles.filter(title__icontains=title)

    if exp_from is not None and exp_to is not None:

        matched_ids = []

        for exp in ProfileExperience.objects.all():
            if exp.yearfrom and exp.yearto:
                years = exp.yearto - exp.yearfrom
                if exp_from <= years <= exp_to:
                    matched_ids.append(exp.profileid)

        filtered_profiles = filtered_profiles.filter(id__in=matched_ids)

    if source_code:
        source_obj = Source.objects.filter(id=source_code).first()
        if source_obj:
            filtered_profiles = filtered_profiles.filter(sourceid=source_obj.id)
        else:
            filtered_profiles = filtered_profiles.none()

   
    if skills:
        skill_profile_ids = (
            ProfileSkills.objects.filter(primaryskills__icontains=skills)
            .values_list("profileid", flat=True)
        )
        filtered_profiles = filtered_profiles.filter(id__in=skill_profile_ids)

    if status:
        filtered_profiles = filtered_profiles.filter(status=status[0])

    if date_from and date_to:
        start_datetime = datetime.strptime(date_from, "%Y-%m-%d")
        end_datetime = datetime.strptime(date_to, "%Y-%m-%d").replace(
            hour=23, minute=59, second=59
        )

        filtered_profiles = filtered_profiles.filter(
            dateofcreation__gte=start_datetime,
            dateofcreation__lte=end_datetime
        )

    status_map = {
        "D": "Draft",
        "R": "Rejected",
        "O": "Offered",
        "E": "Employee",
    }

    final_output = []

    for profile in filtered_profiles:

        # --- EXPERIENCE ---
        exp = ProfileExperience.objects.filter(profileid=profile.id).first()
        years = (exp.yearto - exp.yearfrom) if exp and exp.yearfrom and exp.yearto else 0

        # --- SOURCE ---
        source_value = (
            Source.objects.filter(id=profile.sourceid)
            .values_list("label", flat=True)
            .first() or ""
        )
        strength_val = getattr(profile, 'strength', 0) or 0

        # --- SKILLS (primary + secondary) ---  
        skills_data = (
            ProfileSkills.objects.filter(profileid=profile.id)
            .values("primaryskills", "secondaryskills")
            .first()
        )

        if skills_data:
            primary_sk = skills_data.get("primaryskills") or ""
            secondary_sk = skills_data.get("secondaryskills") or ""
        else:
            primary_sk = ""
            secondary_sk = ""

        # --- APPEND OUTPUT ---
        final_output.append({
            "id":profile.id,
            "date": profile.dateofcreation.strftime("%d-%b-%Y %I:%M %p"),
            "code": profile.profilecode if profile.profilecode else "",
            "title": profile.title if profile.title else " " ,
            "firstname": profile.firstname  if profile.firstname else " ",
            "lastname": profile.lastname if profile.lastname else " ",
            "experience": f"{years} Years",
            "source": source_value,
            "status": const_profile_status.get(profile.status, profile.status),
            "primaryskills_name": primary_sk,
            "secondaryskills_name": secondary_sk,
            "profilestrength": strength_val
        })  

    return JsonResponse({"statusCode": 0, "data": final_output})


@api_view(['GET'])
def getResumeFile(request,rid):

    resume_file = ResumeFile.objects.get(resumeid=rid)

    file_base64 = base64.b64encode(resume_file.filecontent).decode("utf-8")

    return JsonResponse({
        "pdf_data": f"data:application/pdf;base64,{file_base64}"
    })


@api_view(['POST'])
def getFilterResumes(request):
    response = {
        'data': None,
        'error': None,
        'statusCode': 1
    }

    try:
        if request.method == "POST":
            dataObjs = json.loads(request.POST.get('data'))
            user_data = auth_user(request.user)

            resumes_data = getResumeData(user_data,dataObjs)

            response['data'] = resumes_data
            response['statusCode'] = 0

    except Exception as e:
        response['data'] = 'Error in getting filtered resume data'
        response['error'] = str(e)
        raise
    
    return JsonResponse(response)


@api_view(['POST'])
def deleteResume(request):
    response = {
        'data': None,
        'error': None,
        'statusCode': 1
    }
    try:
        if request.method == "POST":
            dataObjs = json.loads(request.POST.get('data'))

            softDeleteResume(dataObjs["resume_id"])

            response['data'] = "success"
            response['statusCode'] = 0

    except Exception as e:
        response['data'] = 'Error in deleting Resume'
        response['error'] = str(e)
        raise
    
    return JsonResponse(response)


@api_view(['POST'])
def addResumeProfile(request):
    response = {
        'data': None,
        'error': None,
        'statusCode': 1
    }
    try:
        if request.method == "POST":
            dataObjs = json.loads(request.POST.get('data'))

            user_data = auth_user(request.user)

            add_profile = addResumeProfileDB(dataObjs,user_data)

            response['data'] = add_profile
            response['statusCode'] = 0

    except Exception as e:
        response['data'] = 'Error in deleting Resume'
        response['error'] = str(e)
        raise
    
    return JsonResponse(response)


@api_view(['POST'])
def addProfile(request):
    response = {
        'data': None,
        'error': None,
        'statusCode': 1
    }
    try:
        if request.method == "POST":
            dataObjs = json.loads(request.POST.get('data'))
            fileObjs = request.FILES.get('attachment')

            user_data = auth_user(request.user)

            addProfileDB(dataObjs,fileObjs,user_data)

            response['data'] = "success"
            response['statusCode'] = 0

    except Exception as e:
        response['data'] = 'Error in saving Profile Details'
        response['error'] = str(e)
        raise
    
    return JsonResponse(response)


@api_view(['POST'])
def updateProfileDetails(request):
    response = {
        'data': None,
        'error': None,
        'statusCode': 1
    }
    try:
        if request.method == "POST":
            dataObjs = json.loads(request.POST.get('data'))

            updateProfileDetailsDB(dataObjs)
            updateProfileCompletion(profile_id=dataObjs["profileid"])

            response['data'] = "success"
            response['statusCode'] = 0

    except Exception as e:
        response['data'] = 'Error in updating Profile Details'
        response['error'] = str(e)
        raise
    
    return JsonResponse(response)


@api_view(['POST'])
def updateProfileEducation(request):
    response = {
        'data': None,
        'error': None,
        'statusCode': 1
    }
    try:
        if request.method == "POST":
            dataObjs = json.loads(request.POST.get('data'))

            updateProfileEducationDB(dataObjs)
            updateProfileCompletion(profile_id=dataObjs["profile_id"])

            response['data'] = "success"
            response['statusCode'] = 0

    except Exception as e:
        response['data'] = 'Error in updating Profile Education Details'
        response['error'] = str(e)
        raise
    
    return JsonResponse(response)


@api_view(['POST'])
def updateProfileExperience(request):
    response = {
        'data': None,
        'error': None,
        'statusCode': 1
    }
    try:
        if request.method == "POST":
            dataObjs = json.loads(request.POST.get('data'))

            updateProfileExperienceDB(dataObjs)
            updateProfileCompletion(profile_id=dataObjs["profile_id"])

            response['data'] = "success"
            response['statusCode'] = 0

    except Exception as e:
        response['data'] = 'Error in updating Profile Experience Details'
        response['error'] = str(e)
        raise
    
    return JsonResponse(response)


@api_view(['POST'])
def updateProfileProjects(request):
    response = {
        'data': None,
        'error': None,
        'statusCode': 1
    }
    try:
        if request.method == "POST":
            dataObjs = json.loads(request.POST.get('data'))

            updateProfileProjectsDB(dataObjs)
            updateProfileCompletion(profile_id=dataObjs["profile_id"])

            response['data'] = "success"
            response['statusCode'] = 0

    except Exception as e:
        response['data'] = 'Error in updating Profile Projects Details'
        response['error'] = str(e)
        raise
    
    return JsonResponse(response)


@api_view(['POST'])
def updateProfileAwards(request):
    response = {
        'data': None,
        'error': None,
        'statusCode': 1
    }
    try:
        if request.method == "POST":
            dataObjs = json.loads(request.POST.get('data'))

            updateProfileAwardsDB(dataObjs)
            updateProfileCompletion(profile_id=dataObjs["profile_id"])

            response['data'] = "success"
            response['statusCode'] = 0

    except Exception as e:
        response['data'] = 'Error in updating Profile Awards Details'
        response['error'] = str(e)
        raise
    
    return JsonResponse(response)


@api_view(['POST'])
def updateProfileCertificates(request):
    response = {
        'data': None,
        'error': None,
        'statusCode': 1
    }
    try:
        if request.method == "POST":
            dataObjs = json.loads(request.POST.get('data'))

            updateProfileCertificatesDB(dataObjs)
            updateProfileCompletion(profile_id=dataObjs["profile_id"])
            response['data'] = "success"
            response['statusCode'] = 0

    except Exception as e:
        response['data'] = 'Error in updating Profile Certificate Details'
        response['error'] = str(e)
        raise
    
    return JsonResponse(response)


@api_view(['POST'])
def updateProfileSkills(request):
    response = {
        'data': None,
        'error': None,
        'statusCode': 1
    }
    try:
        if request.method == "POST":
            dataObjs = json.loads(request.POST.get('data'))

            updateProfileSkillsDB(dataObjs)
            updateProfileCompletion(profile_id=dataObjs["profile_id"])
            response['data'] = "success"
            response['statusCode'] = 0

    except Exception as e:
        response['data'] = 'Error in updating Profile Skills Details'
        response['error'] = str(e)
        raise
    
    return JsonResponse(response)


@api_view(['POST'])
def addProfileActivity(request):
    response = {
        'data': None,
        'error': None,
        'statusCode': 1
    }
    try:
        if request.method == "POST":
            
            user = auth_user(request.user)
            userid=user.id
            dataObjs = json.loads(request.POST.get('data'))

            updateProfileActivityDB(dataObjs,userid)

            response['data'] = "success"
            response['statusCode'] = 0

    except Exception as e:
        response['data'] = 'Error in adding Profile Activity Details'
        response['error'] = str(e)
        raise
    
    return JsonResponse(response)

@csrf_exempt
@api_view(['POST'])
@authentication_classes([])
@permission_classes([])
def candidateProfile(request):
    response = {
        'data': None,
        'error': None,
        'statusCode': 1
    }
    try:
        if request.method == "POST":

            dataObjs = request.POST.dict()
            fileObj = request.FILES.get("attachment")
            

            jd_id = decrypt_code(dataObjs["encjdid"])
            company_id = JobDesc.objects.get(id=jd_id).companyid
          
            if fileObj:
                
                file_binary = fileObj.read()

                ext = os.path.splitext(fileObj.name)[1].lower()

                if ext in [".doc", ".docx"]:
                    
                    try:
                        pdf_binary = convert_word_binary_to_pdf(file_binary)
                    except:
                        pdf_binary = file_binary

                elif ext == ".pdf":
                    pdf_binary = file_binary

                else:
                    raise Exception("Unsupported file format")
                
                filename = fileObj.name
                file_data = pdf_binary
            else:
                filename = None
                file_data = None

            # Example: Get source ID
            # source = Source.objects.filter(code=dataObjs['source-code']).last()
            # sourceid = source.id
            source_code = ""

            if "source-code" in dataObjs:
                
                source = Source.objects.filter(companyid=company_id,code=dataObjs['source-code']).last()
                
                if source:
                    source_code = source.id

                else:
                    new_source = Source(
                        companyid=company_id,
                        code = dataObjs['source-code'],
                        label = dataObjs['source-code']
                    )
                    new_source.save()

                    source_code = new_source.id

            # Save resume header
            new_resume = Resume(
                sourceid = source_code,
                filename = filename,
                mailid = None,                
                companyid = company_id,
                status = "P"
            )
            new_resume.save()

            # Save file content
            if file_data:
                resume_file = ResumeFile(
                    resumeid=new_resume.id,
                    filename=filename,
                    filecontent=file_data
                )
                resume_file.save()

            response['data'] = "Resume uploaded successfully"
            response['statusCode'] = 0

    except Exception as err:
        response['data'] = 'Error in candidateProfile'
        response['error'] = str(err)
        raise

    return JsonResponse(response)


@api_view(['GET'])
def getMailResumes(request):
    response = {
        'data': None,
        'error': None,
        'statusCode': 1
    }
    try:
        if request.method == "GET":
            fetch_gmail_attachments()
            response['data'] = "success"
            response['statusCode'] = 0

    except Exception as e:
        response['data'] = 'Error in getting resume from emails'
        response['error'] = str(e)
        raise
    
    return JsonResponse(response)



@api_view(['POST'])
def sendwelcomemail(request):
    response = {
        'data': None,
        'error': None,
        'statusCode': 1
    }

   

    try:
        profile_id = request.data.get("profile_id")
      

        if not profile_id:
            print(" Missing profile_id")
            response['error'] = "profile_id missing"
            return JsonResponse(response)

   
        profile = Profile.objects.get(id=profile_id)
       

      
        first_name = profile.firstname

        to_email = profile.email
        company_id = profile.companyid

      
        company = Company.objects.get(id=company_id)
       
       
        acert_domain = getConfig()['DOMAIN']['acert']
        endpoint = '/api/get-welcome-mail'
        url = urljoin(acert_domain, endpoint)

        

        payload = {
            "companyId": company_id,
            "toEmail": to_email,
            "first_name": first_name,
          
            "companyName": company.name
        }

        
        acert_res = requests.post(
            url,
            json=payload,
            headers={"Content-Type": "application/json"}
        ).json()
            
        if acert_res.get("statusCode") != 0:
            print(" ACERT email process failed")
            response['error'] = "ACERT email process failed"
            
        response["statusCode"] = 0
        response["data"] = {"email": to_email}

        user=request.user

        acvityuserid = User.objects.get(email=user).id
        
        addProfileActivityDB(profile_id,"E1","Thank you note",acvityuserid)
     

    except Exception as e:
        print(" Exception in sendwelcomemail():", str(e))
        response["error"] = str(e)
    return JsonResponse(response)




@api_view(['POST'])
def check_welcome_mail_status(request):
    response = {"email_sent": False, "statusCode": 1}

    try:
        profile_id = request.data.get("profile_id")
       

        if not profile_id:
            response["error"] = "profile_id missing"
            return JsonResponse(response)

        exists = ProfileActivity.objects.filter(
            profileid=profile_id,
            activitycode="E1"
        ).exists()

        response["email_sent"] = exists
        response["statusCode"] = 0
        return JsonResponse(response)

    except Exception as e:
        response["error"] = str(e)
        return JsonResponse(response)


@api_view(["POST"])
def downloadBrandedProfile(request):
    response = {"data": None, "error": None, "statusCode": 1}
    pdf_file_path = None
    try:
        if request.method == "POST":
            profile_id = request.POST.get("pid")
            user_data = auth_user(request.user)
            pdf_path = generateBrandedProfile(profile_id,user_data)

            pdf_file_path = os.path.normpath(pdf_path['file_path'])
            
            with open(pdf_path['file_path'], 'rb') as pdf_file:
                response = HttpResponse(pdf_file.read(), content_type='application/pdf')
                response['Content-Disposition'] = f'attachment; filename="{pdf_path["file_name"]}.pdf"'

                return response
        
    except Exception as e:
        response["data"] = "Error in downloading profile"
        response["error"] = str(e)

    finally:
        if pdf_file_path:
            if os.path.exists(pdf_file_path):
                os.remove(pdf_file_path)

    return JsonResponse(response)


@api_view(['POST'])
def getworkcal(request):
    response = {
        'data': None,
        'error': None,
        'statusCode': 1
    }

    try:
        body = json.loads(request.POST.get("data"))
        user_id = body.get("user_id")
        company_id = body.get("company_id")

        # Fetch ALL rows
        rows = WorkCal.objects.filter(userid=user_id, companyid=company_id)

        # if not rows.exists():
        #     response['data'] = []
        #     response['weekoff1'] = ""
        #     response['weekoff2'] = ""
        #     response['statusCode'] = 0
        #     return JsonResponse(response)
        if not rows.exists():
            response['data'] = []
            response['statusCode'] = 0
            return JsonResponse(response)

        # Build list
        data = []
        for r in rows:
            data.append({
                "id": r.id,
                "userid": r.userid,
                "companyid": r.companyid,
                "startday": r.startday,
                "starttime": r.starttime.strftime("%H:%M:%S") if r.starttime else None,
                "hours": r.hours,
                # "weekoff1": r.weekoff1,
                # "weekoff2": r.weekoff2
            })

      
        first = rows.first()
        response['weekoff1'] = first.weekoff1
        response['weekoff2'] = first.weekoff2

        response['data'] = data
        response['statusCode'] = 0
        return JsonResponse(response)

    except Exception as e:
        response["error"] = str(e)
        return JsonResponse(response)



@api_view(['POST'])
def saveworkcal(request):
    response = {
        "data": None,
        "error": None,
        "statusCode": 1
    }

    try:
        if request.method == "POST":

            dataObjs = json.loads(request.POST.get("data"))
            

            saveWorkCalDB(dataObjs)

            response["data"] = "success"
            response["statusCode"] = 0

    except Exception as e:
        response["data"] = "Error in saving Details"
        response["error"] = str(e)

    return JsonResponse(response)


@api_view(['POST'])
def delete_work_cal(request, id):
    response = {
        "data": None,
        "error": None,
        "statusCode": 1
    }


    try:
        obj = WorkCal.objects.get(id=id)
        

        obj.delete()
        response["statusCode"] = 0
        response["data"] = "Deleted Successfully"

    except WorkCal.DoesNotExist:
        response["error"] = "Record not found"
        response["statusCode"] = 1

    except Exception as e:
        response["error"] = str(e)
        response["statusCode"] = 1

    return JsonResponse(response)
   


@api_view(['POST'])
def update_jd_status(request):
    response = {"statusCode": 1, "error": None}

    try:
        body = json.loads(request.POST.get("data"))
        print("body",body)
        jd_id = body.get("JdID")
        new_status = body.get("status")
        comments = body.get("comments")  


        jd = JobDesc.objects.get(id=jd_id)
        jd.approval_status = new_status
        if comments is not None:
            jd.comments = comments
  
        
        jd.save()

        response["statusCode"] = 0

    except Exception as e:
        response["error"] = str(e)

    return JsonResponse(response)


@api_view(['POST'])
@authentication_classes([])
@permission_classes([])
def scheduleCandidateInterview(request):
    response = {
        'data': None,
        'error': None,
        'statusCode': 1
    }
    print("scheduleCandidateInterview")
    try:
        if request.method == "POST":
            # user = auth_user(request.user)
            dataObjs = json.loads(request.POST.get('data'))
            res = scheduleCandidateInterviewDB(dataObjs)
            response['data'] = res
            response['statusCode'] = 0

    except Exception as e:
        response['data'] = 'Error in Scheduling Interview'
        response['error'] = str(e)
    return JsonResponse(response) 


@api_view(['POST'])
def scheduleCandidateInterviewLink(request):
    response = {
        'data': None,
        'error': None,
        'statusCode': 1
    }
    try:
        if request.method == "POST":
            dataObjs = json.loads(request.POST.get('data'))
            candidate_id = dataObjs["candidate_id"]
            enc_candidate_id = encrypt_code(candidate_id)
            user_data = auth_user(request.user)
            c_data = scheduleCandidateInterviewLinkDB(enc_candidate_id,user_data)
            response['data'] = c_data
            response['statusCode'] = 0
        else:
            return HttpResponseForbidden('Request Blocked')
       
    except Exception as e:
        response['data'] = 'Error in saving Job Description'
        response['error'] = str(e)
        raise

    return JsonResponse(response)


@api_view(['POST'])
def jdRecruiterAssign(request):

    response = {
        "data": None,
        "error": None,
        "statusCode": 1
    }

    try:
        if request.method == "POST":

            dataObjs = json.loads(request.POST.get("data"))

            jdRecruiterAssignDB(dataObjs)

            response["data"] = "success"
            response["statusCode"] = 0

    except Exception as e:
        response["data"] = "Error in assigning Recruiter to JD"
        response["error"] = str(e)

    return JsonResponse(response)

@api_view(['POST'])
def auto_fill_profile(request):
    response = {
        'data': None,
        'error': None,
        'statusCode': 1
    }

    try:
        if request.method == "POST":
            dataObjs = json.loads(request.POST.get('data'))

            updateFullProfileDB(dataObjs)

            response['data'] = "success"
            response['statusCode'] = 0

    except Exception as e:
        response['data'] = "Error in updating full profile"
        response['error'] = str(e)
        raise
    return JsonResponse(response)


@api_view(['GET'])
def recruiter_dashboard_filter(request):

    response = {
        "statusCode": 1,
        "data": None,
        "error": None
    }

    try:
        company_id = getCompanyId(request.user)

        user_data = auth_user(request.user)
        user_role = user_data.role
        logged_recruiter_id = user_data.id

        selected_recruiter = request.GET.get("recruiter")
        month_value = request.GET.get("month")

        dashboard_data = getRecritmentDashboardData(
            company_id=company_id,
            user_role=user_role,
            logged_recruiter_id=logged_recruiter_id,
            selected_recruiter=selected_recruiter,
            month_value=month_value
        )

        response["data"] = dashboard_data
        response["statusCode"] = 0

    except Exception as e:
        response["error"] = str(e)

    return JsonResponse(response)


@api_view(['POST'])
def addWorkspace(request):

    response = {
        "data": None,
        "error": None,
        "statusCode": 1
    }

    try:
        if request.method == "POST":

            dataObjs = json.loads(request.POST.get("data"))

            user_data = auth_user(request.user)

            addWorkspaceDB(dataObjs,user_data)

            response["data"] = "success"
            response["statusCode"] = 0

    except Exception as e:
        response["data"] = "Error in add new workspace"
        response["error"] = str(e)

    return JsonResponse(response)



@api_view(['POST'])
def jdProfileData(request):

    response = {
        "data": None,
        "error": None,
        "statusCode": 1
    }

    try:
        if request.method == "POST":

            dataObjs = json.loads(request.POST.get("data"))
            user_data = auth_user(request.user)

            jd_profiles_data =  getJdProfileData(dataObjs,user_data)

            response["data"] = jd_profiles_data
            response["statusCode"] = 0

    except Exception as e:
        response["data"] = "Error in getting jd Profile Data"
        response["error"] = str(e)

    return JsonResponse(response)


@api_view(['POST'])
def shortlistProfile(request):

    response = {
        "data": None,
        "error": None,
        "statusCode": 1
    }

    try:
        if request.method == "POST":

            dataObjs = json.loads(request.POST.get("data"))
            user_data = auth_user(request.user)

            shortlist = shortlistProfileService(dataObjs,user_data)
            response["data"] = shortlist
            response["statusCode"] = 0

    except Exception as e:
        response["data"] = "Error in shortlisting the Profile"
        response["error"] = str(e)

    return JsonResponse(response)


@api_view(['GET'])
def dashBoardView(request):
    response = {
        'data': None,
        'error': None,
        'statusCode': 1
    }
    try:
        if request.method == "GET":
            company_id = getCompanyId(request.user)
            user_data = auth_user(request.user)
            user_role = user_data.role
            logged_recruiter_id = user_data.id
            selected_recruiter = request.GET.get("recruiter")
            month_value = request.GET.get("month")
            print("month_value",month_value)

            dashboard_data = dashBoardDataService(company_id=company_id,
            user_role=user_role,
            logged_recruiter_id=logged_recruiter_id,
            selected_recruiter=selected_recruiter,month_value=month_value)
            response['data'] = dashboard_data
            response['statusCode'] = 0


    except Exception as e:
        response['data'] = 'Error in getDashBoardDataService view'
        response['error'] = str(e)
        # logging.error("Error in getDashBoardDataService view : ", str(e))
    return JsonResponse(response)





# @api_view(['GET'])
# def get_profile_strength(request):
#     response = {
#         'data': None,
#         'error': None,
#         'statusCode': 1
#     }
#     try:
#         profile_id = request.GET.get("profile_id")

#         profile = Profile.objects.filter(id=profile_id).values("strength").first()

#         response['data'] = profile["strength"] if profile else 0
#         response['statusCode'] = 0

#     except Exception as e:
#         response['data'] = None
#         response['error'] = str(e)

#     return JsonResponse(response)

@api_view(['GET'])
def get_profile_strength(request):
    try:
        profile_id = request.GET.get("profile_id")
        profile = Profile.objects.filter(id=profile_id).first()

        if profile:
            # Create the dictionary of actual scores
            stats = {
                "strength": profile.strength or 0,
                "educationscore": profile.educationscore or 0,
                "awardsscore": profile.awardsscore or 0,
                "certificatesscore": profile.certificatesscore or 0,
                "experiencescore": profile.experiencescore or 0,
                "projectsscore": profile.projectsscore or 0,
                "skillsscore": profile.skillsscore or 0,
            }
            # Return the dictionary 'stats' as the data key
            return JsonResponse({"statusCode": 0, "data": stats, "error": None})
        
        return JsonResponse({"statusCode": 1, "data": None, "error": "Profile not found"})

    except Exception as e:
        return JsonResponse({"statusCode": 1, "data": None, "error": str(e)})


@api_view(['POST'])
def updateWorkspace(request):

    response = {
        "data": None,
        "error": None,
        "statusCode": 1
    }

    try:
        if request.method == "POST":

            dataObjs = json.loads(request.POST.get("data"))

            updateWorkspaceDB(dataObjs)

            response["data"] = "success"
            response["statusCode"] = 0

    except Exception as e:
        response["data"] = "Error in updating workspace"
        response["error"] = str(e)

    return JsonResponse(response)



@api_view(['POST'])
def addNewClients(request):
    response = {
        'data': None,
        'error': None,
        'statusCode': 1
    }
    try:
        user = auth_user(request.user)
        dataObjs = dataObjs = json.loads(request.POST.get('data'))
        userData = addNewClientService(user.companyid,dataObjs)
        response['data'] = userData
        response['statusCode'] = 0

    except Exception as e:
        response['data'] = 'Error in Creating New User'
        response['error'] = str(e)
        raise
    return JsonResponse(response)






@api_view(['POST'])
def changeClientStatus(request):
    response = {
        'data': None,
        'error': None,
        'statusCode': 1
    }
    try:
        user = auth_user(request.user)
        dataObjs = dataObjs = json.loads(request.POST.get('data'))
        userData = changeClientstatusService(user.companyid,dataObjs)
        response['data'] = userData
        response['statusCode'] = 0

    except Exception as e:
        response['data'] = 'Error in Creating New User'
        response['error'] = str(e)
        raise
    return JsonResponse(response)



@api_view(['POST'])
def recruiters_performance(request):
    try:
        if request.method == "POST":
            user = auth_user(request.user)

            data = json.loads(request.POST.get("data", "{}"))

            from_date = data.get("date_from")
            to_date = data.get("date_to")

            # 2️⃣ Prepare service input
            dataObjs = {
                "cid": user.companyid,   # adjust if different
                "from_date": from_date,
                "to_date": to_date,
            }
            print("dataObjs",dataObjs)
            result = RecruitersPerformanceService(dataObjs)

            return JsonResponse({
                "statusCode": 0,
                "from_date": result["from_date"],
                "to_date": result["to_date"],
                "data": result["data"]
            })

        return JsonResponse({
            "statusCode": 1,
            "data": [],
            "error": "Invalid request method"
        })

    except Exception as e:
        return JsonResponse({
            "statusCode": 1,
            "data": [],
            "error": str(e)
        })
        
        
        

@api_view(['GET'])
def search_jd_library(request):
    try:
        query = request.GET.get("q", "").strip()

        qs = jdlibrary.objects.filter(
            title__icontains=query
        ).values("id", "title")[:10]

        data = list(qs)

        return JsonResponse(data, safe=False)

    except Exception as e:
        return JsonResponse({
            "error": str(e)
        })


@api_view(['GET'])
def jd_library_detail(request):
    try:
        jd_id = request.GET.get("id")

        jd = jdlibrary.objects.get(id=jd_id)

        data = {
            "title": jd.title,
            "description": jd.description or "",
            "role": jd.role or "",
            "min_exp": jd.min_exp or "",
            "max_exp": jd.max_exp or "",
            "work_location": jd.work_location or "",
            "primary_skills": jd.primary_skills if jd.primary_skills else [],
            "secondary_skills": jd.secondary_skills if jd.secondary_skills else [],
        }

        return JsonResponse({
            "status": 1,
            "data": data
        })

    except jdlibrary.DoesNotExist:
        return JsonResponse({
            "status": 0,
            "message": "JD not found"
        })

    except Exception as e:
        return JsonResponse({
            "status": 0,
            "error": str(e)
        })


@api_view(['GET'])
def validate_profile(request):
    try:
        first = request.GET.get("firstname", "").strip()
        middle = request.GET.get("middlename", "").strip()
        last = request.GET.get("lastname", "").strip()
        email = request.GET.get("email", "").strip()
        mobile = request.GET.get("mobile", "").strip()
        profile_id = request.GET.get("profile_id")
        
        company_id = getCompanyId(request.user)


        print("company_id",company_id)

        name_exists = False
        email_exists = False
        mobile_exists = False

        name_profile_code = None
        email_profile_code = None
        mobile_profile_code = None

        
        if email:
            email_obj = Profile.objects.filter(email__iexact=email,  companyid=company_id  )

            if profile_id:
                email_obj = email_obj.exclude(id=profile_id)

            # email_obj = email_obj.first()
            email_obj = email_obj
            if email_obj:
                email_exists = True
                # email_profile_code = email_obj.profilecode
                email_profile_code = list(
                    email_obj.values_list("profilecode", flat=True)
                )


       
        if mobile:
            mobile_obj = Profile.objects.filter(mobile=mobile,   companyid=company_id  )

            if profile_id:
                mobile_obj = mobile_obj.exclude(id=profile_id)

            # mobile_obj = mobile_obj.first()
            mobile_obj = mobile_obj
            if mobile_obj:
                mobile_exists = True
                # mobile_profile_code = mobile_obj.profilecode
                mobile_profile_code = list(
                    mobile_obj.values_list("profilecode", flat=True)
                )

        # if first:
        #     name_obj = Profile.objects.filter(
        #         firstname__iexact=first,
        #         middlename__iexact=middle,
        #         lastname__iexact=last
        #     )
        if first or middle or last:
            name_obj = Profile.objects.filter( companyid=company_id ).filter(
                Q(firstname__iexact=first, middlename__iexact=middle, lastname__iexact=last) |
                Q(firstname__iexact=last, middlename__iexact=middle, lastname__iexact=first)
            )
            if profile_id:
                name_obj = name_obj.exclude(id=profile_id)

            # name_obj = name_obj.first()
            name_obj = name_obj
            if name_obj:
                name_exists = True
                # name_profile_code = name_obj.profilecode
                name_profile_code = list(
                    name_obj.values_list("profilecode", flat=True)
                )


        return JsonResponse({
            "name_exists": name_exists,
            "email_exists": email_exists,
            "mobile_exists": mobile_exists,
            "name_profile_code": name_profile_code,
            "email_profile_code": email_profile_code,
            "mobile_profile_code": mobile_profile_code
        })

    except Exception as e:
        return JsonResponse({
            "status": 0,
            "error": str(e)
        })
    

@api_view(['POST'])
def jobBoardConfig(request):

    response = {
        "data": None,
        "error": None,
        "statusCode": 1
    }

    try:
        if request.method == "POST":

            user = auth_user(request.user)
            dataObjs = json.loads(request.POST.get("data"))

            config_data = jobBoardConfigService(dataObjs,user.companyid)

            response["data"] = config_data
            response["statusCode"] = 0

    except Exception as e:
        response["data"] = "Error in getting Job Board Config"
        response["error"] = str(e)

    return JsonResponse(response)


@api_view(['POST'])
def saveJobBoardConfig(request):

    response = {
        "data": None,
        "error": None,
        "statusCode": 1
    }

    try:
        if request.method == "POST":

            user = auth_user(request.user)
            dataObjs = json.loads(request.POST.get("data"))

            saveJobBoardConfigDB(dataObjs,user.companyid)

            response["data"] = "success"
            response["statusCode"] = 0

    except Exception as e:
        response["data"] = "Error in getting saving Job Board Config"
        response["error"] = str(e)

    return JsonResponse(response)


@api_view(['POST'])
def saveJDJobBoards(request):

    response = {
        "data": None,
        "error": None,
        "statusCode": 1
    }

    try:
        if request.method == "POST":

            user = auth_user(request.user)
            dataObjs = json.loads(request.POST.get("data"))

            saveJDJobBoardsDB(dataObjs,user)

            response["data"] = "success"
            response["statusCode"] = 0

    except Exception as e:
        response["data"] = "Error in saving JD Job Boards"
        response["error"] = str(e)

    return JsonResponse(response)


@api_view(['POST'])
def addResume(request):
    response = {
        'data': None,
        'error': None,
        'statusCode': 1
    }
    try:
        if request.method == "POST":
            dataObjs = json.loads(request.POST.get('data'))
            fileObjs = request.FILES.get('resumefile')

            user_data = auth_user(request.user)

            addResumeDB(dataObjs,fileObjs,user_data)

            response['data'] = "success"
            response['statusCode'] = 0

    except Exception as e:
        response['data'] = 'Error in adding Resume'
        response['error'] = str(e)
        raise
    
    return JsonResponse(response)
