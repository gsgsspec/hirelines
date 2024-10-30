import json
from django.http import JsonResponse
from app_api.functions.hashing import decrypt_code, encrypt_code
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from django.http import HttpResponse, JsonResponse, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt
from allauth.account.utils import perform_login
from allauth.account import app_settings as allauth_settings
from app_api.functions.masterdata import auth_user, getCompanyId

from hirelines.metadata import getConfig, check_referrer
from .functions.services import addCompanyDataService, candidateRegistrationService, registerUserService, authentication_service, getJdWorkflowService,interviewSchedulingService, checkTestHasPaperService, \
        jdTestAdd, addJdServices, updateJdServices, workFlowDataService, interviewCompletionService,questionsResponseService, getInterviewStatusService
from .models import Candidate, Lookupmaster, Registration, User_data, Workflow, InterviewMedia, CallSchedule
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
            addJdServices(dataObjs,companyID,request.user)
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
            workflow_data = Workflow.objects.filter(jobid=jd_id).first()
            if workflow_data:
                company_id = workflow_data.companyid
                dataObjs["jd"] = jd_id
                dataObjs['begin-from'] = workflow_data.paperid
                company_id = 3
                addCandidateDB(dataObjs,company_id,workflow_data)
                response['data'] = 'Registration completed successfully'
            else:
                response['data'] = 'Workflow not defined'
            response['statusCode'] = 0
    except Exception as err:
        response['data'] = 'Error in registerCandidate'
        response['error'] = str(err)
        raise
    print("response",response)
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

    appid = str(dataObjs["reg_code"]).split("_")[1]
    schid = str(dataObjs["reg_code"]).split("_")[2].split(".")[0]

    candidate_details = Candidate.objects.filter(candidateid=appid).last()
    
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
            updateEmailtempDB(user, dataObjs)
            response['data'] = "Email Template updated successfully"
            response['statusCode'] = 0

    except Exception as e:
        response['data'] = 'Error in updateEmailtemp'
        response['error'] = str(e)
    return JsonResponse(response)

