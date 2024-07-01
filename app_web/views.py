from django.shortcuts import render
from app_api.functions import constants

# Create your views here.


def homePage(request):
    try:

        company_types = constants.company_types

        return render(request, "homepage.html", {'company_types': company_types})

    except Exception as e:
        raise