from django.shortcuts import render, redirect
from django.contrib.auth import logout
from django.db.models import Q
from app_api.functions import constants
from app_api.functions.masterdata import user_not_active,auth_user, get_current_path
from app_api.models import User, Role, JobDesc
from app_api.functions.services import getJobDescData, getCandidatesData, getJdCandidatesData, get_functions_service, checkCompanyTrailPeriod

# Create your views here.


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
    
    if checkCompanyTrailPeriod(request.user):
        return redirect('/trial-expired')

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
    if checkCompanyTrailPeriod(request.user):
        return redirect('/trial-expired')
    try:

        return render(request, "portal_index.html", {"template_name": 'email_templates.html'})

    except Exception as e:
        raise



def candidatesPage(request):
    if checkCompanyTrailPeriod(request.user):
        return redirect('/trial-expired')
    try:

        candidates_data = getCandidatesData()

        return render(request, "portal_index.html", {"template_name": 'candidates.html',"candidates_data" : candidates_data})

    except Exception as e:
        raise



def reportsPage(request):

    if not request.user.is_active and not request.user.is_staff:
        return user_not_active(request, after_login_redirect_to=str(request.META["PATH_INFO"]))
    
    if checkCompanyTrailPeriod(request.user):
        return redirect('/trial-expired')

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


def brandingPage(request):
    if checkCompanyTrailPeriod(request.user):
        return redirect('/trial-expired')
    try:

        return render(request, "portal_index.html", {"template_name": 'branding.html'})

    except Exception as e:
        raise



def addCandidatePage(request):
    if checkCompanyTrailPeriod(request.user):
        return redirect('/trial-expired')
    try:

        return render(request, "portal_index.html", {"template_name": 'add_candidate.html'})

    except Exception as e:
        raise



def jdDataPage(request, jid):
    if checkCompanyTrailPeriod(request.user):
        return redirect('/trial-expired')
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
