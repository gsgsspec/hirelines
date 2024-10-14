import json
from django.http import JsonResponse
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from django.http import HttpResponse, JsonResponse, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt
from allauth.account.utils import perform_login
from allauth.account import app_settings as allauth_settings
from app_api.functions.masterdata import auth_user, getCompanyId

from hirelines.metadata import getConfig, check_referrer
from .functions.services import addCompanyDataService, candidateRegistrationService, registerUserService, authentication_service, getJdWorkflowService
from .models import User_data

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
            getJdWorkflowService(jobid,company_id)

    except Exception as e:
        response['data'] = 'Error in getting jd worflow'
        response['error'] = str(e)
        raise
    return JsonResponse(response)