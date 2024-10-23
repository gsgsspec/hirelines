import json
from django.http import JsonResponse
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from django.http import HttpResponse, JsonResponse, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt
from allauth.account.utils import perform_login
from allauth.account import app_settings as allauth_settings
from app_api.functions.masterdata import auth_user, getCompanyId

from hirelines.metadata import getConfig, check_referrer
from .functions.services import addCompanyDataService, candidateRegistrationService, registerUserService, authentication_service, getJdWorkflowService,interviewSchedulingService, jdTestAdd, addJdServices, updateJdServices, workFlowDataService
from .models import User_data
from .functions.database import addCandidateDB, scheduleInterviewDB

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
            print('====================')
            print('user email',request.user)
            print('========================')
            print('dataObjs :: ',dataObjs)
            companyID = getCompanyId(request.user)
            jdTestAdd(dataObjs,companyID)
            response['statusCode'] = 0
    except Exception as e:
        response['data'] = 'Error in adding company data'
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
            c_data = addCandidateDB(dataObjs,company_id,user.id)
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

        else:
            return HttpResponseForbidden('Request Blocked')

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


from django.http import HttpResponse


def candidateRegistrationForm(request, script_id):
    try:
        pass
        # script = JDCandidateRegistrationScripts.objects.get(script_id=script_id)
        # return HttpResponse(script.script_content, content_type='application/javascript')
    except:
        return HttpResponse('console.error("Script not found");', content_type='application/javascript')

