import json
import requests
from datetime import datetime
from urllib.parse import urljoin
from django.db.models import Q
from hirelines.metadata import getConfig
from .mailing import sendEmail
from app_api.models import ReferenceId, Candidate, Registration, CallSchedule, User, JobDesc, Company



def addCompanyDataDB(dataObjs):
    try:
        print('dataObjs')
    except Exception as e:
        raise


def addCandidateDB(dataObjs, cid,user_id):
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

            if c_registration.papertype == 'I':
                call_schedule = CallSchedule(
                    candidateid = candidate.id,
                    hrid = user_id,
                    paper_id = dataObjs['begin-from'],
                    status = 'N',
                    companyid = candidate.companyid
                )
                call_schedule.save()
            
            c_data = {
                'candidateid':candidate.id,
                'papertype':c_registration.papertype
            }

            return c_data

    except Exception as e:
        raise


def scheduleInterviewDB(user_id, dataObjs):
    try:
        call_details = CallSchedule.objects.filter(candidateid=dataObjs['candidate_id']).last()
        if call_details:
            datentime_str = ' '.join(dataObjs['slot_id'].split('__')[:2])
            datentime = datetime.strptime(datentime_str, '%a-%d-%b-%Y %I_%M_%p')  #+ timedelta(hours=5, minutes=30)
            interviewer = dataObjs['slot_id'].split('__')[2:]
            interviewer_id = interviewer[0]

            scheduled_check = CallSchedule.objects.filter(Q(interviewerid=interviewer_id), Q(datentime=datentime),
                                                              Q(status='S')|Q(status='R'))
            user = User.objects.get(id=user_id)
            if not scheduled_check:
                candidate = Candidate.objects.get(id=call_details.candidateid)
                meeting_config = getConfig()['MEETING_CONFIG']['meeting_link']
                string_ = str(interviewer_id) + (str(candidate.candidateid).replace("-", "")) + str(call_details.id)
                enc_st_ = string_.encode('utf-8')
                hex_code = enc_st_.hex()
                meeting_link = meeting_config + hex_code
                call_details.datentime = datentime
                call_details.interviewerid = interviewer_id
                call_details.intnotes = dataObjs['instructions']
                call_details.status = 'S'
                call_details.meetinglink = meeting_link
                call_details.hrid = user_id
                call_details.companyid = user.companyid
                call_details.save()
                
                
                # sendCallScheduleMail(call_details.id)
                # position = Position.objects.get(id=candidate.position_id)
                # paper = Paper.objects.get(id=candidate.paper_id)
                job_desc = JobDesc.objects.get(id=candidate.jobid)
                company = Company.objects.get(id=candidate.companyid)
                # hr = User.objects.get(id=call_details.hrid)
                # interviewer_email = User.objects.get(id=call_details.interviewerid).auth_mail_id
                # emails = f"{candidate.email}, {hr.auth_mail_id}, {interviewer_email}"
                emails = f"{candidate.email}"
                interview_time = call_details.datentime.strftime("%d-%b-%Y %I:%M %p") 


                replacements = {
                    "[candidate_name]": f"{candidate.firstname} {candidate.lastname}",
                    "[job_title]": job_desc.title,
                    "[company_name]": company.name,
                    "[date]": interview_time,
                    "[link]": call_details.meetinglink,
                }

                sendEmail(candidate.companyid,'I',call_details.paper_id,'Call_Schedule',replacements,emails,call_details.datentime)

                return "Slot Booked"
        else:
            return "No Candidate"
    except Exception as e:
        print(str(e))
        raise