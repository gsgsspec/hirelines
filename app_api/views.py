from datetime import datetime
import json
import logging
import time
from urllib.parse import urljoin

import requests
from django.http import JsonResponse
from app_api.functions.enc_dec import decrypt_code, encrypt_code
from hirelines.settings import BASE_DIR
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from django.http import HttpResponse, JsonResponse, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt
from allauth.account.utils import perform_login
from allauth.account import app_settings as allauth_settings
from app_api.functions.masterdata import auth_user, getCompanyId

from hirelines.metadata import getConfig, check_referrer
from .functions.services import addCompanyDataService, candidateRegistrationService, deductCreditsService, registerUserService, authentication_service, getJdWorkflowService,interviewSchedulingService, jdPublishService, \
        jdTestAdd, addJdServices, updateJdServices, workFlowDataService, interviewCompletionService,questionsResponseService, getInterviewStatusService, generateCandidateReport, \
        notifyCandidateService,checkTestHasPaperService, deleteTestInJdService, saveInterviewersService,generateCandidateReport

        
from .models import Account, Branding, Candidate, CompanyCredits, JobDesc, Lookupmaster, Registration, User_data, Workflow, InterviewMedia, CallSchedule
from .functions.database import addCandidateDB, scheduleInterviewDB, interviewResponseDB, addInterviewFeedbackDB, updateEmailtempDB
from app_api.functions.constants import hirelines_registration_script

# Create your views here.

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
        response['data'] = 'Error in adding company data'
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
        response['data'] = 'Error in adding company data'
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
            #Filter the first workflow obj to attend first paper $ order functionality not added $
            job_description = JobDesc.objects.get(id=jd_id)
            if job_description.status == "A":
                workflow_data = Workflow.objects.filter(jobid=jd_id,order=1).last()
                if workflow_data:
                    company_id = workflow_data.companyid
                    dataObjs["jd"] = jd_id
                    dataObjs['begin-from'] = workflow_data.paperid
                    company_id = workflow_data.companyid
                    addCandidateDB(dataObjs,company_id,workflow_data)
                    response['data'] = 'Registration completed successfully'
                else:
                    response['data'] = 'Workflow not defined'
            else:
                response['data'] = 'JD inactive'
            response['statusCode'] = 0
    except Exception as err:
        response['data'] = 'Error in registerCandidate'
        response['error'] = str(err)
        raise
    print("response",response)
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
                            response['data'] = "Result Mail Sent to Candidate Successfully"
                            response['statusCode'] = 0
                else:                
                    response['data'] = "Query Not Found"
                    response['statusCode'] = 0

        
    except Exception as e:
        response['data'] = 'Error in evaluationquestionsView'
        response['error'] = str(e)
        raise
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
    return JsonResponse(response)

@api_view(['POST'])
def saveInterviewersForJs(request):
    response = {
        'data': None,
        'error': None,
        'statusCode': 1
    }
    try:
        if request.method == "POST":
            user = auth_user(request.user)
            dataObjs = json.loads(request.POST.get('data'))
            saveInterviewersService(user, dataObjs)
            
            response['statusCode'] = 0

    except Exception as e:
        response['data'] = 'Error in Deleting Test from workflow'
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
            notifyCandidateService(dataObjs)
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
                if company_account.balance >= company_credits.credits:
                    response['data'] = "credits_available"
                else:
                    response['data'] = "insufficient_credits"
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
            if company_account.balance<1000:
                low_credits =  "Y"
            else:
                low_credits = "N"
                
            company_account_obj = {
                "balance_credits":company_account.balance,
                "low_credits":low_credits
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
                company_branding.sociallinks=dataObjs['social_links']
                company_branding.status = dataObjs['status']
                company_branding.save()
                logo_file_path = ""
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
    return JsonResponse({"name": user.name})

    
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
                candidate = Candidate.object.get(candidateid=decrypt_code(dataObjs["participant_refid"]),
                                                 companyid=company_id)
                registration = Registration.objects.filter(companyid=company_id,
                                                           candidateid=candidate.id,
                                                           jobid=candidate.jobid,
                                                           papertype=dataObjs["paper_type"],
                                                           paperid=decrypt_code(dataObjs["paper_id"])).last()
                registration.status = dataObjs["update_value"]
                registration.save()
                
                response['data'] = "Registration status updated successfully"
                response['statusCode'] = 0
                
            if dataObjs["update_type"] == "candidate_status":
                candidate = Candidate.object.get(candidateid=decrypt_code(dataObjs["participant_refid"]),
                                                 companyid=company_id)
                candidate.status = dataObjs["update_value"]
                candidate.save()
                response['data'] = "candidate status updated successfully"
                response['statusCode'] = 0
            
            if dataObjs["update_type"] == "add_registration":
                
                candidate = Candidate.object.get(candidateid=decrypt_code(dataObjs["participant_refid"]),
                                                 companyid=company_id)
                
                paper_id = decrypt_code(dataObjs["paper_id"])
                
                registration = Registration(companyid=company_id,
                                                           candidateid=candidate.id,
                                                           jobid=candidate.jobid,
                                                           papertype=dataObjs["paper_type"],
                                                           paperid=paper_id,
                                                           registrationdate=datetime.now(),
                                                           status="P")
                registration.save()
                
                if dataObjs["paper_type"] == 'I':
                    job_desc = JobDesc.object.get(id=candidate.jobid)
                    call_schedule = CallSchedule(
                        candidateid = candidate.id,
                        hrid = job_desc.createdby,
                        paper_id = paper_id,
                        status = 'N',
                        companyid = candidate.companyid
                    )
                    
                    call_schedule.save()

                response['data'] = "Registered successfully"
                response['statusCode'] = 0

    except Exception as e:
        response['data'] = 'Error in getUpdateCompanyCreditsView'
        response['error'] = str(e)
        # raise
    return JsonResponse(response)