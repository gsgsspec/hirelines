import json
import requests
from datetime import datetime
from urllib.parse import urljoin
from hirelines.metadata import getConfig
from app_api.models import ReferenceId, Candidate, Registration



def addCompanyDataDB(dataObjs):
    try:
        print('dataObjs')
    except Exception as e:
        raise


def addCandidateDB(dataObjs, cid):
    try:

        candidate = Candidate(
            firstname = dataObjs["firstname"],
            lastname = dataObjs["lastname"],
            companyid = cid,
            email = dataObjs["email"],
            mobile = dataObjs["mobile"],
            jobid = dataObjs["jd"],
            registrationdate = datetime.now(),
            status = 'P'
        )

        year = datetime.now().strftime("%y")

        refid_obj, refid_flag = ReferenceId.objects.get_or_create(type = "R", prefix1 = "{:03}".format(cid), prefix2 = year)
            
        if refid_flag == True:
            lastid = 1
            refid_obj.lastid = lastid
            refid_obj.save()

        if refid_flag == False:
            lastid = refid_obj.lastid+1
            refid_obj.lastid = lastid
            refid_obj.save()

        candidate_id_seq = str('{:05}'.format(int(refid_obj.lastid)))
        candidate_code = f"{refid_obj.prefix1}{refid_obj.prefix2}{candidate_id_seq}"

        candidate.candidateid = candidate_code

        candidate.save()

        acert_domain = getConfig()['DOMAIN']['acert']
        endpoint = '/api/hirelines-add-candidate'

        url = urljoin(acert_domain, endpoint)

        candidate_data = {
            'firstname' : dataObjs["firstname"],
            'lastname' : dataObjs["lastname"],
            'email':dataObjs["email"],
            'mobile': dataObjs["mobile"],
            'paper_id': dataObjs['begin-from'], 
            'company_id':cid,
            'reference_id': candidate.candidateid
        }

        send_candidate_data = requests.post(url, json = candidate_data)
        response_content = send_candidate_data.content

        if response_content:
            json_data = json.loads(response_content.decode('utf-8'))

            acert_data = json_data['data']
            print('acert_data',acert_data)

            c_registration = Registration(
                candidateid = candidate.id,
                paperid = dataObjs['begin-from'],
                registrationdate = candidate.registrationdate,
                companyid = candidate.companyid,
                jobid = candidate.jobid,
                status = 'P',
                papertype = acert_data["papertype"],
            )

            c_registration.save()
            
            c_data = {
                'candidateid':candidate.id,
                'papertype':c_registration.papertype
            }

            return c_data

    except Exception as e:
        raise
