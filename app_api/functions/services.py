from datetime import datetime

from .constants import public_email_domains
from app_api.models import CompanyData, JobDesc, Candidate, Registration



def addCompanyDataService(dataObjs):
    try:

        bussiness_email = str(dataObjs['reg-bemail'])

        email_domain = bussiness_email.split('@')[1]

        if email_domain in public_email_domains:
            return 1
        
        email_check = CompanyData.objects.filter(companyemail=bussiness_email)

        if email_check:
            return 2

        company_data = CompanyData(
            companyname = dataObjs["reg-company"],
            companyemail = bussiness_email,
            location = dataObjs['reg-location'],
            contactperson = dataObjs["reg-name"],
            companytype = dataObjs["reg-companytype"],
            registerationtime = datetime.now()
        )
        company_data.save()
        
        return 0


    except Exception as e:
        raise



def getJobDescData(jid):
    try:

        job_desc = JobDesc.objects.filter(id=jid).last()

        if job_desc:

            screening_tests = Registration.objects.filter(companyid=1,jobid=jid,papertype='S').count()
            coding_tests = Registration.objects.filter(companyid=1,jobid=jid,papertype='E').count()
            interviews = Registration.objects.filter(companyid=1,jobid=jid,papertype='I').count()
            offer_letters = Registration.objects.filter(companyid=1,jobid=jid,papertype='I',status='O').count()

            jd_data = {
                'title' : job_desc.title,
                'screening_tests':screening_tests,
                'coding_tests':coding_tests,
                'interviews':interviews,
                'offer_letters':offer_letters
            }


            return jd_data


    except Exception as e:
        raise



def candidateRegistrationService(dataObjs):
    try:

        fname =  dataObjs['fname']
        lname =  dataObjs['lname']
        email =  dataObjs['email']
        mobile =  dataObjs['mobile']
        paper_id =  dataObjs['paper_id']
        company_id =  dataObjs['company_id']

        candidate = Candidate(
            firstname = fname,
            lastname = lname,
            companyid = company_id,
            paperid = paper_id,
            email = email,
            mobile = mobile
        )
        # candidate.save()

    except Exception as e:
        raise



def getJdCandidatesData(jid):
    try:   

        candidates = Candidate.objects.filter(jobid=jid,companyid=1)

        candidates_data = []

        for candidate in candidates:

            registrations = Registration.objects.filter(candidateid=candidate.id,companyid=candidate.companyid)

            candidate_info = {
                'id': candidate.id,
                'cid':candidate.candidateid,
                'name': candidate.firstname,
                'email': candidate.email,
                'registrations': {'S':[],'E':[],'I':[]}
            }

            for registration in registrations:

                registration_info = {
                    'date': registration.registrationdate.strftime("%Y-%m-%d"),
                    'status': registration.status,
                }

                if registration.papertype == 'S':
                    candidate_info['registrations']['S'].append(registration_info)
                elif registration.papertype == 'E':
                    candidate_info['registrations']['E'].append(registration_info)
                elif registration.papertype == 'I':
                    candidate_info['registrations']['I'].append(registration_info)

            candidates_data.append(candidate_info)

        return candidates_data

    except Exception as e:
        raise



def getCandidatesData():
    try:

        candidates_list = []

        candidates = Candidate.objects.all().order_by("-id")

        for candidate in candidates:

            candidates_list.append({
                'candidate_id': candidate.candidateid,
                'firstname': candidate.firstname,
                'lastname': candidate.lastname,
                'email' : candidate.email
            })

        return candidates_list

    except Exception as e:
        raise