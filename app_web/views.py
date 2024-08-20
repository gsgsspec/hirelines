from django.shortcuts import render
from app_api.functions import constants
from app_api.models import JobDesc

from app_api.functions.services import getJobDescData, getCandidatesData, getJdCandidatesData

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
    try:

        return render(request, "portal_index.html", {"template_name": 'dashboard.html'})

    except Exception as e:
        raise



def emailTemplatesPage(request):
    try:

        return render(request, "portal_index.html", {"template_name": 'email_templates.html'})

    except Exception as e:
        raise



def candidatesPage(request):
    try:

        candidates_data = getCandidatesData()

        return render(request, "portal_index.html", {"template_name": 'candidates.html',"candidates_data" : candidates_data})

    except Exception as e:
        raise



def reportsPage(request):
    try:

        job_descriptions = JobDesc.objects.all()

        return render(request, "portal_index.html", {"template_name": 'reports.html',"job_descriptions":job_descriptions})

    except Exception as e:
        raise


def brandingPage(request):
    try:

        return render(request, "portal_index.html", {"template_name": 'branding.html'})

    except Exception as e:
        raise



def addCandidatePage(request):
    try:

        return render(request, "portal_index.html", {"template_name": 'add_candidate.html'})

    except Exception as e:
        raise



def jdDataPage(request, jid):
    try:

        jd_data = getJobDescData(jid)

        candidates_data = getJdCandidatesData(jid)

        return render(request, "portal_index.html", {"template_name": 'jd_data.html','jd_data':jd_data,'candidates_data':candidates_data})

    except Exception as e:
        raise
