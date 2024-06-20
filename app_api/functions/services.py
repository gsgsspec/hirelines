from .constants import public_email_domains
from app_api.models import CompanyData



def addCompanyDataService(dataObjs):
    try:

        bussiness_email = str(dataObjs['reg-bemail'])

        email_domain = bussiness_email.split('@')[1]

        if email_domain in public_email_domains:
            return 1
        
        email_check = CompanyData.objects.filter(company_email=bussiness_email)

        if email_check:
            return 2

        company_data = CompanyData(
            company_name = dataObjs["reg-company"],
            company_email = bussiness_email,
            location = dataObjs['reg-location']
        )
        company_data.save()
        
        return 0


    except Exception as e:
        raise