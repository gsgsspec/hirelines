import json
import requests
from datetime import datetime
from urllib.parse import urljoin
from django.db.models import Q
from app_api.functions.enc_dec import decrypt_code

from hirelines.metadata import getConfig
from .mailing import sendEmail
from app_api.models import Account, Brules, CompanyCredits, ReferenceId, Candidate, Registration, CallSchedule, User, JobDesc, Company,CompanyData,Workflow, QResponse, \
    IvFeedback, Email_template


def addCompanyDataDB(dataObjs):
    try:
        print('dataObjs')
    except Exception as e:
        raise


def addCandidateDB(dataObjs, cid,workflow_data, user_id=None):
    try:
        from app_api.functions.services import deductCreditsService
        company_account = Account.objects.get(companyid=cid)
        workflow = Workflow.objects.filter(companyid= cid,paperid=dataObjs['begin-from']).last()
        company_credits = CompanyCredits.objects.get(companyid=cid,transtype=workflow.papertype)
        if company_account.balance >= company_credits.credits:
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
                    status = 'I',
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
                
                # Removed, because the this process has to handled by ACERT
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
                deductCreditsService(cid,acert_data["papertype"],dataObjs['begin-from'])
                return c_data
        else:
            return "insufficient_credits"
    except Exception as e:
        raise


def scheduleInterviewDB(user_id, dataObjs):
    try:
        user = User.objects.get(id=user_id)
        company_account = Account.objects.get(companyid=user.companyid)
        company_credits = CompanyCredits.objects.get(companyid=user.companyid,transtype="I")
        if company_account.balance >= company_credits.credits:
            call_details = CallSchedule.objects.filter(candidateid=dataObjs['candidate_id']).last()
            if call_details:
                datentime_str = ' '.join(dataObjs['slot_id'].split('__')[:2])
                datentime = datetime.strptime(datentime_str, '%a-%d-%b-%Y %I_%M_%p') 
                interviewer = dataObjs['slot_id'].split('__')[2:]
                interviewer_id = interviewer[0]

                scheduled_check = CallSchedule.objects.filter(Q(interviewerid=interviewer_id), Q(datentime=datentime),
                                                                Q(status='S')|Q(status='R'))
                

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
                    call_details.instructions = dataObjs['instructions']
                    call_details.status = 'S'
                    call_details.meetinglink = meeting_link
                    call_details.hrid = user_id
                    call_details.companyid = user.companyid
                    call_details.save()

                    # Mail Replacements
                    job_desc = JobDesc.objects.get(id=candidate.jobid)
                    interview_time = call_details.datentime.strftime("%d-%b-%Y %I:%M %p") 

                    interviewer = User.objects.get(id=call_details.interviewerid)
                    to_mails = f"{candidate.email},{interviewer.email}"

                    interview_data = {
                        'job_title':job_desc.title,
                        'meetinglink':call_details.meetinglink,
                        'int_paper': call_details.paper_id,
                        'candidate_code': candidate.candidateid,
                        'interviewer': call_details.interviewerid,
                        'interview_time': interview_time,
                        'to_emails': to_mails
                    }

                    acert_domain = getConfig()['DOMAIN']['acert']
                    endpoint = '/api/schedule-interview'

                    url = urljoin(acert_domain, endpoint)

                    send_interview_data = requests.post(url, json=interview_data)

                    # replacements = {
                    #     "[candidate_name]": f"{candidate.firstname} {candidate.lastname}",
                    #     "[job_title]": job_desc.title,
                    #     "[company_name]": company.name,
                    #     "[date]": interview_time,
                    #     "[link]": call_details.meetinglink,
                    # }
                    

                    # Email Function

                    # sendEmail(candidate.companyid,'I',call_details.paper_id,'Call_Schedule',replacements,emails,call_details.datentime)

                    return "Slot Booked"
            else:
                return "No Candidate"
        else:
            return "insufficient_credits"
    except Exception as e:
        print(str(e))
        raise

    
def saveJdNewTest(dataObjs,compyId):
    try:

        if dataObjs['createOrUpdate'] == 'create': # it create new Test.
            
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

        if dataObjs['createOrUpdate'] == 'update': # it will update the existing Test

            if 'testId' in dataObjs:
                currentTestId = dataObjs['testId']

            if currentTestId:
                savedWorkFlowDetails = Workflow.objects.filter(id = currentTestId, companyid = compyId, jobid = dataObjs['jdId']).last()
                brulesData = Brules.objects.filter(companyid = compyId,workflowid = savedWorkFlowDetails.id, jobdescid = dataObjs['jdId']).last()
                
                if 'testName' in dataObjs:
                    if dataObjs['testName']:
                        savedWorkFlowDetails.papertitle = dataObjs['testName']
                
                if 'createdPaperid' in dataObjs:
                    if savedWorkFlowDetails.paperid == None:
                        savedWorkFlowDetails.paperid = dataObjs['createdPaperid']
                        brulesData.paperid = dataObjs['createdPaperid']
                        brulesData.save()
                
                if 'libraryId' in dataObjs:
                    if dataObjs['libraryId']:
                        savedWorkFlowDetails.paperlibraryid = dataObjs['libraryId']

                savedWorkFlowDetails.save()

                passcore = ''
                if 'promotPercentage' in dataObjs:
                    if dataObjs['promotPercentage']:
                        brulesDetails = Brules.objects.filter(companyid = compyId, jobdescid = dataObjs['jdId'], workflowid = currentTestId).last()
                        if brulesDetails:
                            brulesDetails.passscore = dataObjs['promotPercentage']
                            passcore = brulesDetails.passscore
                            brulesDetails.save()
                        else:
                            save_bruls = Brules(
                                companyid = compyId,
                                jobdescid = dataObjs['jdId'],
                                workflowid = currentTestId,
                                passscore = dataObjs['promotPercentage']
                            )
                            save_bruls.save()

                updatedData = {   
                   'updateEvent': 'Y',
                    'companyid' : compyId,
                    'id'        : savedWorkFlowDetails.id,
                    'jobid'     : savedWorkFlowDetails.jobid,
                    'order'     : None,
                    'paperid'   : savedWorkFlowDetails.paperid,
                    'papertitle': savedWorkFlowDetails.papertitle,
                    'papertype' : savedWorkFlowDetails.papertype,
                    'promot'    : passcore
                }

                return dict(updatedData)

    except Exception as e:
        raise

# delete test in jd
def deleteTestInJdDB(dataObjs,):
    try:
        workflowDetails = Workflow.objects.filter(jobid=dataObjs['jdid'])
        testIdList = list(workflowDetails.values_list('id', flat=True))
        workflowDetails = list(workflowDetails.values())
        
        if workflowDetails:
            for testInWorkFlow in range(0, len(workflowDetails)):

                # If the ID matches, perform delete or other action
                if workflowDetails[testInWorkFlow]['id'] == dataObjs['deleteTestId']:
                    deleteTest = Workflow.objects.filter(id=workflowDetails[testInWorkFlow]['id']).last()
                    if deleteTest:
                        delBrules = Brules.objects.filter(workflowid = deleteTest.id,jobdescid = deleteTest.jobid).last()
                        if deleteTest:
                            deleteTest.delete()
                        if delBrules:
                            delBrules.delete()
                        else:
                            ''
                            # Brules Not Found

                        nextSelectedCard = 0
                        if testInWorkFlow == 0:
                            
                            if(len(testIdList) >= 2):
                                nextSelectedCard = testIdList[testInWorkFlow + 1] # return this if first card deleted
                        else:
                            if(testInWorkFlow + 1) == len(testIdList):
                                if(testInWorkFlow + 1) <= len(testIdList):
                                    nextSelectedCard = testIdList[testInWorkFlow - 1] # return this if last card deleted and there is another in fornt of card

                            if(testInWorkFlow + 1) <= len(testIdList) and len(testIdList) >= (testInWorkFlow + 1):
                                nextSelectedCard = testIdList[testInWorkFlow - 1] # return this if last card deleted 

                        return {'msg':'Deleted-successfully','testData':workflowDetails[testInWorkFlow],'nextSelectTestId':nextSelectedCard}
                    else:
                        ''
                        # No workflow find

        # if dataObjs['deleteTestId']:
        #     getTestData = Workflow.objects.filter(id = dataObjs['deleteTestId']).last()
        #     testData = {}
        #     if getTestData:
        #         testData['testid']= getTestData.id
        #         testData['paperType'] = getTestData.papertype
        #         # getTestData.delete()
        #         print('Deleted Succssfully')

        #         return {'msg':'Deleted-successfully','testData':testData}

    except Exception as e:
        raise



# Saving the Job descritption Deatils
def saveInterviewersJD(dataObjs):
    try:
        if dataObjs['jdId']:
            jdData = JobDesc.objects.filter(id = dataObjs['jdId']).last()
            if dataObjs['interviwersLst']:
                jdData.interviewers = dataObjs['interviwersLst']
                jdData.save()
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
                department  = dataObjs['role'] if dataObjs['role'] else None,
                expmin      = dataObjs['minExp'] if dataObjs['minExp'] else None,
                expmax      = dataObjs['maxExp'] if dataObjs['maxExp'] else None,
                location    = dataObjs['workLocation'] if dataObjs['workLocation'] else None,
                budget      = dataObjs['budget'] if dataObjs['budget'] else None,
                positions   = dataObjs['noPositions'] if dataObjs['noPositions'] else None,
                createdby   = hrDeatils.id if hrDeatils.id else None,
                skillset    = dataObjs['skills'] if dataObjs['skills'] else None, 
                skillnotes  = dataObjs['anySpecialNote'] if dataObjs['anySpecialNote'] else None, 
                companyid   = compyId if compyId else None,
                status      = 'D',
                createdon = datetime.now()
            )
            saveJd.save()

            return {'newJdId':saveJd.id}
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

        candidate = Candidate.objects.get(id=dataObjs["candid_id"])

        call_schedule = CallSchedule.objects.get(id=dataObjs["call_sch_id"]) 

        response_data = {
            'qid': dataObjs["qid"],
            'qrate':dataObjs['qrate'],
            'candidate_code': candidate.candidateid,   
            'int_paper': call_schedule.paper_id  
        }

        acert_domain = getConfig()['DOMAIN']['acert']
        endpoint = '/api/interview-response'

        url = urljoin(acert_domain, endpoint)

        send_response_data = requests.post(url, json=response_data)
            
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


def updateEmailtempDB(user,dataObjs,fileObjs):
    try:
        paper_type = 'S' if dataObjs['paper_type'] == "Screening" else 'E' if dataObjs['paper_type'] == "Coding" else "I" if dataObjs['paper_type'] == "Interview" else ''
        email_temp = Email_template.objects.filter(company_id=decrypt_code(dataObjs['company_id']),event=dataObjs['event'],paper_type=paper_type).last()
        if email_temp:
            email_temp.template_heading = dataObjs['template_heading']
            email_temp.email_subject = dataObjs['email_subject']
            email_temp.email_body = dataObjs['email_body']
            email_temp.template_name = dataObjs['template_name']
            email_temp.template_heading = dataObjs['template_heading']
            email_temp.sender_label = dataObjs['sender_label']
            email_temp.email_attachment=dataObjs['attachment_name']
            email_temp.email_attachment_name=dataObjs['file_name']
            email_temp.save()
            if dataObjs["update_remove_attachment"] == "remove":
                email_temp.email_attachment_path = None
                email_temp.email_attachment = None
                email_temp.email_attachment_name = None
                email_temp.save() 
        else:
            email_temp = Email_template(
                company_id = decrypt_code(dataObjs['company_id']),
                email_subject = dataObjs['email_subject'],
                email_body = dataObjs['email_body'],
                template_name = dataObjs['template_name'],
                template_heading = dataObjs['template_heading'],
                sender_label = dataObjs['sender_label'],
                event = dataObjs['event'],
                paper_type = paper_type,
                email_attachment=dataObjs['attachment_name'],
                email_attachment_name=dataObjs['file_name']
            )
            email_temp.save()
            if dataObjs["update_remove_attachment"] == "remove":
                email_temp.email_attachment_path = None
                email_temp.email_attachment = None
                email_temp.email_attachment_name = None
                email_temp.save()
        template = Email_template.objects.filter(company_id=decrypt_code(dataObjs['company_id']),event=dataObjs['event'],paper_type=paper_type).latest('id')
        for file in fileObjs.items():
            template.email_attachment_path = file[1]
        template.save()

    except Exception as e:
        raise


