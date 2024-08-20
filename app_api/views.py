import json
from django.http import JsonResponse
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from django.http import HttpResponse, JsonResponse, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt

from hirelines.metadata import getConfig, check_referrer
from .functions.services import addCompanyDataService, candidateRegistrationService


# Create your views here.


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

    return JsonResponse(response)



@csrf_exempt
@api_view(['POST'])
@authentication_classes([])
@permission_classes([])
def company_paper_registration(request):
    response = {
        'data': None,
        'error': None,
        'statusCode': 1
    }

    try:
        if request.method == "POST" and check_referrer(request):

            dataObjs = json.loads(request.body)

            candidateRegistrationService(dataObjs)

            response['data'] = "Details Saved Sucessfully"
            response['statusCode'] = 0

        else:
            return HttpResponseForbidden('Request Blocked')
        
    except Exception as e:
           response['data'] = 'Error in Registration'
           response['error'] = str(e)
           raise
    return JsonResponse(response)