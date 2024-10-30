import json
import requests
from datetime import datetime
from urllib.parse import urljoin
from django.db.models import Q
from hirelines.metadata import getConfig
from .mailing import sendEmail
from app_api.models import Brules, ReferenceId, Candidate, Registration, CallSchedule, User, JobDesc, Company,CompanyData,Workflow, QResponse, \
    IvFeedback, Email_template


def addCompanyDataDB(dataObjs):
    try:
        print('dataObjs')
    except Exception as e:
        raise


def addCandidateDB(dataObjs, cid,workflow_data, user_id=None):
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
        candidate.save()
        company_data = Company.objects.get(id=cid)
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
        # Adding candidate at acert via api
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

        send_candidate_data = requests.post(url, json = candidate_data, verify=False)
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
            
            # Removed, because the company 
            # 
            # replacements = {
            #     "[candidate_name]": f"{candidate.firstname} {candidate.lastname if candidate.lastname else ''}",
            #     "[paper_name]": acert_data["paper_name"],
            #     "[company_name]": company_data.name,
            #     "[recruitment_email_address]": company_data.email,
            #     "[exam_link]":acert_data["exam_url"],
            #     "[deadline]": acert_data["deadline"]
            # }
            # if workflow_data.papertype == "I":
            #     sendEmail(candidate.companyid,workflow_data.papertype,dataObjs['begin-from'],'Call_Schedule',replacements,candidate.email)
            # else:
            #     sendEmail(candidate.companyid,workflow_data.papertype,dataObjs['begin-from'],'Registration',replacements,candidate.email)
            return c_data
    except Exception as e:
        raise


def scheduleInterviewDB(user_id, dataObjs):
    try:
        call_details = CallSchedule.objects.filter(candidateid=dataObjs['candidate_id']).last()
        if call_details:
            datentime_str = ' '.join(dataObjs['slot_id'].split('__')[:2])
            datentime = datetime.strptime(datentime_str, '%a-%d-%b-%Y %I_%M_%p') 
            interviewer = dataObjs['slot_id'].split('__')[2:]
            interviewer_id = interviewer[0]

            scheduled_check = CallSchedule.objects.filter(Q(interviewerid=interviewer_id), Q(datentime=datentime),
                                                              Q(status='S')|Q(status='R'))
            user = User.objects.get(id=user_id)

            # Updating Not scheduled Call

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
                
                # Mail Replacements
                job_desc = JobDesc.objects.get(id=candidate.jobid)
                company = Company.objects.get(id=candidate.companyid)
                emails = f"{candidate.email}"
                interview_time = call_details.datentime.strftime("%d-%b-%Y %I:%M %p") 


                replacements = {
                    "[candidate_name]": f"{candidate.firstname} {candidate.lastname}",
                    "[job_title]": job_desc.title,
                    "[company_name]": company.name,
                    "[date]": interview_time,
                    "[link]": call_details.meetinglink,
                }

                # Email Function

                sendEmail(candidate.companyid,'I',call_details.paper_id,'Call_Schedule',replacements,emails,call_details.datentime)

                return "Slot Booked"
        else:
            return "No Candidate"
    except Exception as e:
        print(str(e))
        raise

    
def saveJdNewTest(dataObjs,compyId):
    try:

        if dataObjs['createOrUpdate'] == 'create':
            
            testType = None
            if 'testType' in dataObjs:
                if dataObjs['testType'] == 'Screening':
                    testType = 'S'
                if dataObjs['testType'] == 'Coding':
                    testType = 'E'
                if dataObjs['testType'] == 'Interview':
                    testType = 'I'

            savedWorkFlowDetails = Workflow(
                    companyid = compyId,
                    jobid = dataObjs['jdId'] if 'jdId' in dataObjs else None,
                    paperid = None,
                    papertype = testType,
                    papertitle = dataObjs['testName'] if 'testName' in dataObjs else None,
                    )
            savedWorkFlowDetails.save()
            
            wrkflId = savedWorkFlowDetails.id
            # workFlowDetails = Workflow.objects.filter(id = wrkflId).last()
            # workFlowDetails.values()
            workFlowDetails = Workflow.objects.filter(id=wrkflId).values().last()

            save_bruls = Brules(
                    companyid = compyId,
                    jobdescid = dataObjs['jdId'],
                    workflowid = wrkflId,
                    passscore = dataObjs['promotPercentage']
                    )
            save_bruls.save()
            workFlowDetails['promot'] = save_bruls.passscore

            return [workFlowDetails]

        if dataObjs['createOrUpdate'] == 'update':

            if 'testId' in dataObjs:
                currentTestId = dataObjs['testId']

            if currentTestId:
                savedWorkFlowDetails = Workflow.objects.filter(id = currentTestId, companyid = compyId, jobid = dataObjs['jdId']).last()
                savedWorkFlowDetails.papertitle = dataObjs['testName']
                savedWorkFlowDetails.save()

                brulesDetails = Brules.objects.filter(companyid = compyId, jobdescid = dataObjs['jdId'], workflowid = currentTestId).last()
                brulesDetails.passscore = dataObjs['promotPercentage']
                brulesDetails.save()

                updatedData = {   
                   'updateEvent': 'Y',
                    'companyid' : compyId,
                    'id'        : savedWorkFlowDetails.id,
                    'jobid'     : savedWorkFlowDetails.jobid,
                    'order'     : None,
                    'paperid'   : 49,
                    'papertitle': savedWorkFlowDetails.papertitle,
                    'papertype' : savedWorkFlowDetails.papertype,
                    'promot'    : brulesDetails.passscore
                }

                return dict(updatedData)

    except Exception as e:
        raise


# Saving the Job descritption Deatils
def saveAddJD(dataObjs,compyId,hrEmail):
    try:
        hrDeatils = User.objects.filter(email=hrEmail).last()
        if hrDeatils is not None:
            saveJd = JobDesc(
                jdlibraryid = dataObjs['jdLibraryId'] if dataObjs['jdLibraryId'] else None,
                title       = dataObjs['title'] if dataObjs['title'] else None,
                description = dataObjs['jobDesc'] if dataObjs['jobDesc'] else None,
                role        = dataObjs['role'] if dataObjs['role'] else None,
                expmin      = dataObjs['minExp'] if dataObjs['minExp'] else None,
                expmax      = dataObjs['maxExp'] if dataObjs['maxExp'] else None,
                location    = dataObjs['workLocation'] if dataObjs['workLocation'] else None,
                budget      = dataObjs['budget'] if dataObjs['budget'] else None,
                positions   = dataObjs['noPositions'] if dataObjs['noPositions'] else None,
                createdby   = hrDeatils.id if hrDeatils.id else None,
                skillset    = dataObjs['skills'] if dataObjs['skills'] else None, 
                skillnotes  = dataObjs['anySpecialNote'] if dataObjs['anySpecialNote'] else None, 
                companyid   = compyId if compyId else None,
                status      = 'O'
            )
            saveJd.save()
    except Exception as e:
        raise

# Updating the Job descriptions Details
def saveUpdateJd(dataObjs, compyId, hrEmail):
    try:
        hrDetails = User.objects.filter(email=hrEmail).last()
        if hrDetails is not None:
            # Check if the JobDesc with the given jdLibraryId exists
            jobDesc = JobDesc.objects.filter(id = dataObjs['JdID']).first()
            if jobDesc:
                # Update the fields only if the JobDesc exists
                jobDesc.title       = dataObjs['title'] if dataObjs['title'] else None
                jobDesc.description = dataObjs['jobDesc'] if dataObjs['jobDesc'] else None
                jobDesc.role        = dataObjs['role'] if dataObjs['role'] else None
                jobDesc.expmin      = dataObjs['minExp'] if dataObjs['minExp'] else None
                jobDesc.expmax      = dataObjs['maxExp'] if dataObjs['maxExp'] else None
                jobDesc.location    = dataObjs['workLocation'] if dataObjs['workLocation'] else None
                jobDesc.budget      = dataObjs['budget'] if dataObjs['budget'] else None
                jobDesc.positions   = dataObjs['noPositions'] if dataObjs['noPositions'] else None
                jobDesc.skillset    = dataObjs['skills'] if dataObjs['skills'] else None
                jobDesc.skillnotes  = dataObjs['anySpecialNote'] if dataObjs['anySpecialNote'] else None
                jobDesc.companyid   = compyId if compyId else None
                jobDesc.createdby   = hrDetails.id if hrDetails.id else None
                jobDesc.status      = 'O'  # 'O' is the open status for JD
                # Save the updated JobDesc
                jobDesc.save()
    except Exception as e:
        print(f"Error occurred: {e}")
        raise


def interviewResponseDB(dataObjs):
    try:
        try:
            res_check = QResponse.objects.get(qid=dataObjs["qid"],candidateid=dataObjs["candid_id"],callscheduleid=dataObjs["call_sch_id"])
        except:
            res_check = None

        if res_check:

            QResponse(id = res_check.id,
                qid = dataObjs["qid"],
                candidateid = dataObjs["candid_id"],
                callscheduleid = dataObjs["call_sch_id"],
                qrate = dataObjs["qrate"]
            ).save()

        else:
            QResponse(qid = dataObjs["qid"],
                candidateid = dataObjs["candid_id"],
                callscheduleid = dataObjs["call_sch_id"],
                qrate = dataObjs["qrate"]
            ).save()  
            
    except Exception as e:
        raise


def addInterviewFeedbackDB(user,dataObjs):
    try:
        
        try:
            feedback = IvFeedback.objects.filter(candidateid=dataObjs["candidateid"],interviewerid=user.id).last()
            feedback.gonogo = dataObjs['gonogo']
            feedback.notes = dataObjs['notes']
            feedback.companyid = user.companyid
            feedback.save()

        except:
            feedback = IvFeedback(
                candidateid = dataObjs["candidateid"],
                interviewerid = user.id,
                gonogo = dataObjs['gonogo'],
                notes = dataObjs['notes'],
                companyid = user.companyid
            )

            feedback.save()

    except Exception as e:
        raise


def updateEmailtempDB(user,dataObjs):
    try:
        paper_type = 'S' if dataObjs['paper_type'] == "Screening" else 'E' if dataObjs['paper_type'] == "Coding" else "I" if dataObjs['paper_type'] == "Interview" else ''
        email_temp = Email_template.objects.filter(company_id=dataObjs['id'],event=dataObjs['event'],paper_type=paper_type).last()
        if email_temp:
            email_temp.email_subject = dataObjs['email_subject']
            email_temp.email_body = dataObjs['email_body']
            email_temp.template_name = dataObjs['template_name']
            email_temp.template_heading = dataObjs['id']
            email_temp.sender_label = dataObjs['sender_label']
            email_temp.template_heading = dataObjs['template_heading']

        else:
            Email_template(
                company_id = dataObjs['id'],
                email_subject = dataObjs['email_subject'],
                email_body = dataObjs['email_body'],
                template_name = dataObjs['template_name'],
                template_heading = dataObjs['template_heading'],
                sender_label = dataObjs['sender_label'],
                event = dataObjs['event'],
                paper_type = paper_type
            ).save()

    except Exception as e:
        raise


