import os
import json
import requests
from datetime import datetime
from urllib.parse import urljoin, unquote
from django.db.models import Q, Max
from app_api.functions.enc_dec import decrypt_code

from hirelines.metadata import getConfig
from .mailing import sendEmail
from app_api.models import Account, Brules, CompanyCredits, ReferenceId, Candidate, Registration, CallSchedule, User, JobDesc, Company,CompanyData,Workflow, QResponse, \
    IvFeedback, Email_template, Branding, Source, Profile, Resume, ProfileAwards, ProfileActivity, ProfileEducation, ProfileExperience, ProfileProjects, ProfileSkills, ProfileCertificates, \
    ResumeFile, WorkCal,ProfileAddress,Lookupmaster,Workspace
from django.db import transaction

from .doc2pdf import convert_word_binary_to_pdf

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

        app_config = getConfig()['APP_CONFIG']
        register_candidate_once_per_jd = app_config["register_candidate_once_per_jd"]
        if register_candidate_once_per_jd == "N":
            check_candidate_registered = "N"
        else:
            check_candidate_registered = Candidate.objects.filter(companyid = cid,
                jobid = dataObjs["jd"],
                email = dataObjs["email"])

        if (not check_candidate_registered) or (check_candidate_registered == "N"):
            
            if company_account.balance >= company_credits.credits:

                source_code = ""

                if "source-code" in dataObjs:
                    
                    source = Source.objects.filter(companyid=cid,code=dataObjs['source-code']).last()
                    
                    if source:
                        source_code = source.code

                    else:
                        new_source = Source(
                            companyid=cid,
                            code = dataObjs['source-code'],
                            label = dataObjs['source-code']
                        )
                        new_source.save()

                        source_code = new_source.code
                    
                candidate = Candidate(
                    firstname = dataObjs["firstname"],
                    lastname = dataObjs["lastname"],
                    companyid = cid,
                    email = dataObjs["email"],
                    mobile = dataObjs["mobile"],
                    jobid = dataObjs["jd"],
                    source = source_code,
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

                jd_title = ''
                jd_desc = ''

                jd_details = JobDesc.objects.filter(id=dataObjs["jd"]).last()
                if jd_details:
                    jd_title = jd_details.title or ''
                    jd_desc = jd_details.description or ''

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
                    'reference_id': candidate.candidateid,
                    'jd_title':jd_title,
                    'jd_desc':jd_desc
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
                    
                    deductCreditsService(cid,acert_data["papertype"],dataObjs['begin-from'])
                    
                    credit_availablity_stat = "N"

                    if company_account.balance >= company_credits.credits:
                        credit_availablity_stat = "Y"
                        current_credits = company_account.balance-company_credits.credits
                    else:
                        credit_availablity_stat = "N"
                        current_credits = company_account.balance
                    app_config = getConfig()['APP_CONFIG']
                    lowcredits_warning = int(app_config["lowcredits_warning"])
                    reg_stop_warning = int(app_config["reg_stop_warning"])
                    if current_credits<=reg_stop_warning:
                        credits_status =  "N"
                    elif current_credits<=lowcredits_warning:
                        credits_status = "L"
                    else:
                        credits_status = "A"
                    send_lowcredits_notification = "N"
                    if (credits_status ==  "N") or (credits_status == "L"):
                        if company_account.lowcreditsnotification != "Y":
                            send_lowcredits_notification = "Y"
                            company_account_ = Account.objects.get(companyid=cid)
                            company_account_.lowcreditsnotification = "Y"
                            company_account_.save()

                            hr_admin_label = "HR-Admin"
                            hradmin_emails_list = list(User.objects.filter(companyid=cid,role__contains=hr_admin_label,status="A").values_list("email",flat=True))
                            credits_info = {
                                "company_id":cid,
                                "credit_availablity_stat":credit_availablity_stat,
                                "credits_status":credits_status,
                                "hradmin_emails_list":hradmin_emails_list,
                                "current_credits":current_credits,
                                "send_lowcredits_notification":send_lowcredits_notification
                            }
                            acert_domain = getConfig()['DOMAIN']['acert']
                            # credits-notification at acert via api
                            endpoint = '/api/credits-notification'
                            credits_notification_url = urljoin(acert_domain, endpoint)
                            credits_notification_request = requests.post(credits_notification_url, json = credits_info, verify=False)
                            credits_notification_resp = credits_notification_request.content

                            if credits_notification_resp:
                                
                                credits_notification_resp_obj = json.loads(credits_notification_resp.decode('utf-8'))
                    return c_data
            else:
                return "insufficient_credits"
        else:
            return 'candidate_already_registered'
    except Exception as e:
        raise


def scheduleInterviewDB(user_id, dataObjs):
    try:
        user = User.objects.get(id=user_id)
        raw_cid = str(dataObjs.get('candidate_id'))
        # company_account = Account.objects.get(companyid=user.companyid)
        # company_credits = CompanyCredits.objects.get(companyid=user.companyid,transtype="I")
        # if company_account.balance >= company_credits.credits:
        # encrypted_cid = unquote(dataObjs.get('candidate_id'))
        # dataObjs['candidate_id'] = encrypted_cid
        # dataObjs['candidate_id'] = decrypt_code(dataObjs['candidate_id'])
        if raw_cid.isdigit():
            # If it's just numbers (e.g., "432"), use it directly
            dataObjs['candidate_id'] = raw_cid
        else:
            # If it's not a number, assume it's encrypted and decrypt it
            encrypted_cid = unquote(raw_cid)
            dataObjs['candidate_id'] = decrypt_code(encrypted_cid)
        call_details = CallSchedule.objects.filter(candidateid=dataObjs['candidate_id']).last()
        if call_details:    
            datentime_str = ' '.join(dataObjs['slot_id'].split('__')[:2])
            datentime = datetime.strptime(datentime_str, '%a-%d-%b-%Y %I_%M_%p') 
            interviewer = dataObjs['slot_id'].split('__')[2:]
            interviewer_id = interviewer[0]
            
            scheduled_check = CallSchedule.objects.filter(Q(interviewerid=interviewer_id), Q(datentime=datentime),
                                                            Q(status='S')|Q(status='R'))
            
            print("scheduled_check",scheduled_check)
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
                    'to_emails': to_mails,
                    'instructions': call_details.instructions,
                    'schedule_type':dataObjs['schedule_type']
                }

                acert_domain = getConfig()['DOMAIN']['acert']
                endpoint = '/api/schedule-interview'

                url = urljoin(acert_domain, endpoint)

                send_interview_data = requests.post(url, json=interview_data)
                if candidate.profileid:
                    # 1. Check if an 'Interview Scheduled' record already exists for this profile
                    interview_exists = ProfileActivity.objects.filter(
                        profileid=candidate.profileid, 
                        activitycode="IS"
                    ).exists()

                    if interview_exists:
                        # 2. If it exists, record it as "Re-Scheduled"
                        addProfileActivityDB(candidate.profileid, "RS", "Interview Re-Scheduled", user.id)
                    else:
                        # 3. If it does NOT exist, record it as "Interview Scheduled"
                        addProfileActivityDB(candidate.profileid, "IS", "Interview Scheduled", user.id)
                return "Slot Booked"
            else: 
                return "Please select another slot"
        else:
            return "No Candidate"
        # else:
        #     return "insufficient_credits"
    except Exception as e:
        print(str(e))
        raise

    
def saveJdNewTest(dataObjs,compyId):
    try:
        print('dataObjs',dataObjs)
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
                    teststatus = 'A'
                    )
            savedWorkFlowDetails.save()
            
            wrkflId = savedWorkFlowDetails.id
            
            workFlowDetails = Workflow.objects.filter(id=wrkflId).values().last()

            holdStatus = None
            if 'holdYesOrNo' in dataObjs:
                holdStatus = dataObjs['holdYesOrNo']
            
            # holdpercentagval = None
            # if 'holdvalue' in dataObjs:
            #     holdpercentagval = dataObjs['holdvalue']

            holdpercentagval = 0
            if 'holdvalue' in dataObjs:
                if dataObjs['holdvalue']:
                    holdpercentagval = int(dataObjs['holdvalue'])

            save_bruls = Brules(
                        companyid = compyId,
                        jobdescid = dataObjs['jdId'],
                        workflowid = wrkflId,
                        passscore = dataObjs['promotPercentage'],
                        hold = holdStatus,
                        holdpercentage = holdpercentagval,
                    )
            save_bruls.save()
            workFlowDetails['promot'] = save_bruls.passscore
            workFlowDetails['hold'] = dataObjs['holdYesOrNo']
            workFlowDetails['holdpercentage'] = ''
            if 'holdvalue' in dataObjs:
                if dataObjs['holdvalue']:
                    workFlowDetails['holdpercentage'] = dataObjs['holdvalue']

            return [workFlowDetails]
        
        # it will update the existing Test.
        if dataObjs['createOrUpdate'] == 'update': 

            holdStatus = None
            if 'holdYesOrNo' in dataObjs:
                holdStatus = dataObjs['holdYesOrNo']
            
            holdpercentagval = 0
            if 'holdvalue' in dataObjs:
                if dataObjs['holdvalue']:
                    holdpercentagval = int(dataObjs['holdvalue'])

            if 'testId' in dataObjs:
                currentTestId = dataObjs['testId']

            if currentTestId:
                savedWorkFlowDetails = Workflow.objects.filter(id = currentTestId, companyid = compyId, jobid = dataObjs['jdId']).last()
                brulesData = Brules.objects.filter(companyid = compyId,workflowid = savedWorkFlowDetails.id, jobdescid = dataObjs['jdId']).last()
                
                if 'testName' in dataObjs:
                    if dataObjs['testName']:
                        savedWorkFlowDetails.papertitle = dataObjs['testName']
                        savedWorkFlowDetails.save()
                
                if 'createdPaperid' in dataObjs:
                    savedWorkFlowDetails.paperid = dataObjs['createdPaperid']
                    savedWorkFlowDetails.save()

                    brulesData.paperid = dataObjs['createdPaperid']
                    brulesData.save()
                
                if 'libraryId' in dataObjs:
                    if dataObjs['libraryId']:
                        savedWorkFlowDetails.paperlibraryid = dataObjs['libraryId']
                        savedWorkFlowDetails.save()

                passcore = ''
                if 'promotPercentage' in dataObjs:
                    if dataObjs['promotPercentage']:
                        brulesDetails = Brules.objects.filter(companyid = compyId, workflowid = currentTestId , jobdescid = dataObjs['jdId']).last()
                        passcore = dataObjs['promotPercentage']

                        if brulesDetails:
                            brulesDetails.hold = holdStatus
                            brulesDetails.holdpercentage = holdpercentagval
                            brulesDetails.passscore = dataObjs['promotPercentage']
                            brulesDetails.save()

                        else:
                            save_bruls = Brules(
                                companyid = compyId,
                                jobdescid = dataObjs['jdId'],
                                workflowid = currentTestId,
                                hold = holdStatus,
                                holdpercentage = holdpercentagval,
                                passscore = dataObjs['promotPercentage'],
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
                    'promot'    : passcore,
                    'hold'      : holdStatus,
                    'holdpercentage' : holdpercentagval
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
                    paperId = ''
                    if deleteTest:
                        paperId = deleteTest.paperid

                        if deleteTest:
                            deleteTest.delete()

                        delBrules = Brules.objects.filter(workflowid = deleteTest.id,jobdescid = deleteTest.jobid).last()
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

                        return {'msg':'Deleted-successfully','testData':workflowDetails[testInWorkFlow],'nextSelectTestId':nextSelectedCard, 'paperId':paperId}
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

                return {'interviewers':jdData.interviewers}
    except Exception as e:
        raise


# Saving the Job descritption Deatils
def saveAddJD(dataObjs,compyId,hrEmail):
    try:
        # skillsArry = str(dataObjs['skills']).replace('[', '').replace(']', '').replace("'", '').replace('"', '')
        hiringmanager= dataObjs['hiringmanager']
        hrDeatils = User.objects.filter(email=hrEmail).last()
        if hrDeatils is not None:
            saveJd = JobDesc(
                # jdlibraryid = dataObjs['jdLibraryId'] if dataObjs['jdLibraryId'] else None,
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
                skillset    = dataObjs['skills'], 
                secondaryskills    = dataObjs['secondarySkills'], 
                skillnotes  = dataObjs['anySpecialNote'] if dataObjs['anySpecialNote'] else None, 
                companyid   = compyId if compyId else None,
                status      = 'D',
                hiringmanagerid= hiringmanager if hiringmanager else None,
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
            # skillsArry = str(dataObjs['skills']).replace('[', '').replace(']', '').replace("'", '').replace('"', '')
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
                jobDesc.skillset    = dataObjs['skills']
                jobDesc.secondaryskills    = dataObjs['secondarySkills']
                jobDesc.skillnotes  = dataObjs['anySpecialNote'] if dataObjs['anySpecialNote'] else None
                jobDesc.companyid   = compyId if compyId else None
                jobDesc.createdby   = hrDetails.id if hrDetails.id else None
                jobDesc.status      = dataObjs['jobDescriptionStatus']
                jobDesc.hiringmanagerid= dataObjs['hiringmanager'] if dataObjs['hiringmanager'] else None
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



def interviewRemarkSaveDB(dataObjs):
    try:

        call_schedule = CallSchedule.objects.get(id=int(dataObjs["sch_id"]))
        call_schedule.intnotes = dataObjs["remarks"]
        call_schedule.save()
            
    except Exception as e:
        raise


def saveStarQuestion(dataObjs):
    try:
        if dataObjs['testCardId']:
            workFlowData = Workflow.objects.filter(id = dataObjs['testCardId']).last()
            if workFlowData:
                dataObjs['paperid'] = workFlowData.paperid
            else:
                return {'msg':'test paper id was not found'}
        else:
            return {'msg':'test number was not found'}
        
        acert_domain = getConfig()["DOMAIN"]["acert"]
        endpoint = "/api/star-question"

        url = urljoin(acert_domain, endpoint)

        startQuestionData = {
            'data':dataObjs
        }

        requests.post(url, json=startQuestionData)
            
    except Exception as e:
        raise


def updateCompanyDB(dataObjs):
    try:

        company = Company.objects.get(id=dataObjs['cid'])

        company.name = dataObjs['company-name']
        company.contactperson = dataObjs['contact-person']
        company.email = dataObjs['company-email']
        company.phone1 = dataObjs['phone']
        company.website = dataObjs['website']
        company.city = dataObjs['city']
        company.address1 = dataObjs['location']
        company.country = dataObjs['country']
        company.companytype = dataObjs['companytype']

        company.save()

        social_links = []
        for key in ['Linkedin', 'Facebook', 'Instagram', 'Youtube', 'Twitter']:
            if dataObjs.get(key):
                social_links.append(f"{key}:{dataObjs[key]}")

        social_links_string = ', '.join(social_links) + ',' if social_links else ''

        branding = Branding.objects.filter(companyid=company.id).last()

        if branding:
            branding.sociallinks = social_links_string
            branding.save()

        acert_domain = getConfig()["DOMAIN"]["acert"]
        endpoint = "/api/update-company"

        url = urljoin(acert_domain, endpoint)

        company_data = {
            'data':dataObjs,
            'social_links': social_links_string
        }

        send_company_data = requests.post(url, json=company_data)
        
    except Exception as e :
        raise


def demoRequestDB(dataObjs):
    try:
        
        company_data = CompanyData.objects.filter(id=dataObjs['demo-id']).last()

        if company_data:
            company_data.demorequest = "Y"
            company_data.save()

    except Exception as e:
        raise


def deleteCandidateDB(dataObjs):
    try:

        delete_candidates = dataObjs['cid']

        if delete_candidates:
            for candidate_id in delete_candidates:
                candidate = Candidate.objects.filter(id=candidate_id).last()
                if candidate:
                    candidate.deleteflag = "Y"
                    candidate.save()

    except Exception as e:
        raise


def updateSourcesDataDB(dataObjs, company_id):
    try:

        sources_data = dataObjs['sources_data']

        for source in sources_data:

            company_source = Source.objects.filter(companyid=company_id,code=source['code']).last()
            if company_source:
                company_source.label = source['label']
                company_source.save()

    except Exception as e:
        raise


def updateCandidateInfoDB(dataObjs, company_id):
    try:

        candidate = Candidate.objects.filter(candidateid=dataObjs['cid'],companyid=company_id).last()

        if candidate:
            candidate.firstname = dataObjs['firstname']
            candidate.lastname = dataObjs['lastname']
            candidate.mobile = dataObjs['mobile']

            candidate.save()

    except Exception as e:
        raise


def updateDashboardDisplayFlagDB(dataObjs, company_id):
    try:

        job_desc = JobDesc.objects.filter(id=dataObjs['jobid'],companyid=company_id).last()
        
        if job_desc:
            job_desc.dashboardflag = dataObjs['dashboard-display']
            job_desc.save()

    except Exception as e:
        raise


def addResumeProfileDB(dataObjs,user_data):
    try:

        resume = Resume.objects.get(id=dataObjs["resume_id"])

        profile = Profile(
            sourceid = resume.sourceid,
            resumeid = resume.id,
            companyid = resume.companyid,
            dateofcreation = datetime.now(),
            status = "D",
        )

        profile.save()

        resume.status = "A"
        resume.save()

        # activity_data = {
        #     "profileid":profile.id,
        #     "acvityuserid": user_data.id,
        # }
        
        # createProfileActivityDB(activity_data)
        addProfileActivityDB(profile.id,"PC","Profile Created",user_data.id)

        return {"profile_id":profile.id}

    except Exception as e:
        raise



def addProfileDB(dataObjs,fileObjs, user_data):
    try:

        sourceid = None

        file_binary = fileObjs.read()

        ext = os.path.splitext(fileObjs.name)[1].lower()

        if ext in [".doc", ".docx"]:
            
            try:
                pdf_binary = convert_word_binary_to_pdf(file_binary)
            except:
                pdf_binary = file_binary

        elif ext == ".pdf":
            pdf_binary = file_binary

        else:
            raise Exception("Unsupported file format")

        source = Source.objects.filter(companyid=user_data.companyid,code=dataObjs['source-code']).last()
        
        if source:
            sourceid = source.id

        else:
            new_source = Source(
                companyid=user_data.companyid,
                code = dataObjs['source-code'],
                label = dataObjs['source-code']
            )
            new_source.save()

            sourceid = new_source.id

        resume = Resume(
            sourceid = sourceid,
            companyid = user_data.companyid,
            filename = fileObjs.name,
            datentime = datetime.now(),
            status = "A"
        )

        resume.save()

        resume_file = ResumeFile(
            resumeid = resume.id,
            filename = fileObjs.name,
            filecontent = pdf_binary
        )

        resume_file.save()

        profile = Profile(
            sourceid = sourceid,
            resumeid = resume.id,
            companyid = user_data.companyid,
            dateofcreation = datetime.now(),
            title = dataObjs["title"],
            firstname = dataObjs["firstname"],
            middlename = dataObjs["middlename"],
            lastname = dataObjs["lastname"],
            email = dataObjs["email"],
            status = "D"
        )

        profile.save()

        activity_data = {
            "profileid":profile.id,
            "acvityuserid": user_data.id,
        }
        
        # createProfileActivityDB(activity_data)
        addProfileActivityDB(profile.id,"PC","Profile Created",user_data.id)

    except Exception as e:
        raise


def updateProfileDetailsDB(dataObjs):
    try:

        profile = Profile.objects.get(id=dataObjs["profileid"])
        profile_address, created = ProfileAddress.objects.get_or_create(
            profileid=dataObjs["profileid"]
        )

        profile.title = dataObjs["title"]
        profile.firstname = dataObjs["firstname"]
        profile.middlename = dataObjs["middlename"]
        profile.lastname = dataObjs["lastname"]
        profile.email = dataObjs["email"]
        profile.mobile = dataObjs["mobile"]
        profile.linkedin = dataObjs["linkedin"]
        profile.facebook = dataObjs["facebook"]
        profile.passportnum = dataObjs["passport"]
        profile.fathername = dataObjs["father_name"]
        profile.nativeof = dataObjs["native_of"]

        profile_address.addline1 = dataObjs["AddressLine1"]
        profile_address.addline2 = dataObjs["AddressLine2"]
        profile_address.city = dataObjs["city"]
        profile_address.state = dataObjs["state"]
        profile_address.country = dataObjs["country"]
        profile_address.zipcode = dataObjs["zipcode"]
        profile_address.profileid = profile.id
        profile_address.save()

        dob_str = dataObjs["dob"]
        if dob_str:
            profile.dateofbirth = datetime.strptime(dob_str, "%Y-%m-%d").date()
        else:
            profile.dateofbirth = None

        profile.save()

    except Exception as e:
        raise


def updateProfileEducationDB(dataObjs):
    try:
        from app_api.functions.profile_strength import CalculateProfileScoring
        profile_id = dataObjs["profile_id"]
        profile_education = dataObjs["data"]

        ProfileEducation.objects.filter(profileid=profile_id).delete()

        for index,education in enumerate(profile_education, start=1):

            ProfileEducation.objects.create(
                profileid=profile_id,
                sequence = index,
                course = education["coursename"],
                institute = education["institutename"],
                yearfrom = education["yearfrom"],
                yearto = education["yearto"],
                grade = education["grade"]
            )
            
        updateProfileScoreDB(profile_id)
        
    except Exception as e:
        raise


def updateProfileExperienceDB(dataObjs):
    try:
        
        profile_id = dataObjs["profile_id"]
        profile_experience = dataObjs["data"]

        ProfileExperience.objects.filter(profileid=profile_id).delete()

        for index,experience in enumerate(profile_experience, start=1):

            ProfileExperience.objects.create(
                profileid=profile_id,
                sequence = index,
                jobtitle = experience["jobtitle"],
                company = experience["companyname"],
                yearfrom = experience["yearfrom"],
                yearto = experience["yearto"],
            )
        
        updateProfileScoreDB(profile_id)

    except Exception as e:
        raise


def updateProfileProjectsDB(dataObjs):
    try:

        profile_id = dataObjs["profile_id"]
        profile_projects = dataObjs["data"]

        ProfileProjects.objects.filter(profileid=profile_id).delete()

        for index,project in enumerate(profile_projects, start=1):

            ProfileProjects.objects.create(
                profileid=profile_id,
                sequence = index,
                projectname = project["projectname"],
                clientname = project["clientname"],
                roleplayed = project["roleplayed"],
                skillsused = project["skillsused"],
                yearsfrom = project["yearfrom"],
                yearsto = project["yearto"],
            )
        
        updateProfileScoreDB(profile_id)

    except Exception as e:
        raise


def updateProfileAwardsDB(dataObjs):
    try:

        profile_id = dataObjs["profile_id"]
        profile_awards = dataObjs["data"]

        ProfileAwards.objects.filter(profileid=profile_id).delete()

        for index,award in enumerate(profile_awards, start=1):

            ProfileAwards.objects.create(
                profileid=profile_id,
                sequence = index,
                awardname = award["awardname"],
                year = award["year"]
            )
        
        updateProfileScoreDB(profile_id)

    except Exception as e:
        raise


def updateProfileCertificatesDB(dataObjs):
    try:

        profile_id = dataObjs["profile_id"]
        profile_certificates = dataObjs["data"]

        ProfileCertificates.objects.filter(profileid=profile_id).delete()

        for index,certificate in enumerate(profile_certificates, start=1):

            ProfileCertificates.objects.create(
                profileid=profile_id,
                sequence = index,
                certname = certificate["cert_name"],
                year = certificate["year"]
            )
        
        updateProfileScoreDB(profile_id)

    except Exception as e:
        raise


def updateProfileSkillsDB(dataObjs):
    try:

        profile_id = dataObjs["profile_id"]
        profile_skills = dataObjs["skills"]

        ProfileSkills.objects.filter(profileid=profile_id).delete()

        skills_str = ",".join(profile_skills)

        ProfileSkills.objects.create(
            profileid=profile_id,
            primaryskills=skills_str
        )
        
        updateProfileScoreDB(profile_id)

    except Exception as e:
        raise


def updateProfileActivityDB(dataObjs,userid):
    try:
        profile_id = dataObjs.get("profile_id")
        
        activityname = dataObjs.get("activityname")
       
        remarks = dataObjs.get("remarks")
       
       
        lookup = Lookupmaster.objects.filter(lookupname=activityname,status='A').first()
      

        if not lookup:
            raise Exception("Invalid activity name")

        activity_code = lookup.lookupparam1   
      

    
        last_seq = ProfileActivity.objects.filter(profileid=profile_id).aggregate( max_seq=Max('sequence'))['max_seq']
     
        next_seq = (last_seq or 0) + 1
        


        companyid=None
        if profile_id:
            companyid= Profile.objects.get(id=profile_id).companyid
        ProfileActivity.objects.create(
            profileid=profile_id,
            sequence=next_seq,
            datentime=datetime.now(),
            acvityuserid=userid,
            activityname=activityname,
            activitycode=activity_code,
            activityremarks=remarks,
            companyid=companyid

        )

        return True

    except Exception as e:
        raise


def saveWorkCalDB(dataObjs):
    try:
        user_id = dataObjs.get("userid")
        
        
        company_id = dataObjs.get("companyid")
       
        items = dataObjs.get("items", [])
     
 

        if not items:
            raise Exception("No rows provided")

        weekoff1 = items[0].get("weekoff1")
       
        weekoff2 = items[0].get("weekoff2")
        

        for item in items:

            row_id = item.get("id")

            if row_id:
                # UPDATE existing row
                WorkCal.objects.filter(id=row_id).update(
                    startday=item.get("startday"),
                    starttime=item.get("starttime"),
                    hours=item.get("hours"),
                    weekoff1=weekoff1,
                    weekoff2=weekoff2
                )
            else:
                # INSERT new row
                WorkCal.objects.create(
                    userid=user_id,
                    companyid=company_id,
                    startday=item.get("startday"),
                    starttime=item.get("starttime"),
                    hours=item.get("hours"),
                    weekoff1=weekoff1,
                    weekoff2=weekoff2
                )

        return True

    except Exception as e:
        print("saveWorkCalDB ERROR:", str(e))
        raise


def scheduleInterviewLinkDB(user_id, dataObjs):
    try:
        user = User.objects.get(id=user_id)
        # company_account = Account.objects.get(companyid=user.companyid)
        # company_credits = CompanyCredits.objects.get(companyid=user.companyid,transtype="I")
        # if company_account.balance >= company_credits.credits:

        call_details = CallSchedule.objects.filter(candidateid=dataObjs['candidate_id']).last()
        if call_details:    
            datentime_str = ' '.join(dataObjs['slot_id'].split('__')[:2])
            datentime = datetime.strptime(datentime_str, '%a-%d-%b-%Y %I_%M_%p') 
            interviewer = dataObjs['slot_id'].split('__')[2:]
            interviewer_id = interviewer[0]
            
            scheduled_check = CallSchedule.objects.filter(Q(interviewerid=interviewer_id), Q(datentime=datentime),
                                                            Q(status='S')|Q(status='R'))
            
            print("scheduled_check",scheduled_check)
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
                    'to_emails': to_mails,
                    'instructions': call_details.instructions,
                    'schedule_type':dataObjs['schedule_type']
                }

                acert_domain = getConfig()['DOMAIN']['acert']
                endpoint = '/api/schedule-interview'

                url = urljoin(acert_domain, endpoint)

                send_interview_data = requests.post(url, json=interview_data)

                return "Slot Booked"
        else:
            return "No Candidate"
        # else:
        #     return "insufficient_credits"
    except Exception as e:
        print(str(e))
        raise



def scheduleCandidateInterviewLinkDB(enc_candidate_id,user_data):
    try:
        candidate_id = decrypt_code(enc_candidate_id)
        candidate_details=Candidate.objects.get(id=candidate_id)
        # CallSchedule.objects.filter(candidateid=candidate_id).update(status='W')
        
        acert_domain = getConfig()['DOMAIN']['acert']
        hirelines_domain = getConfig()['DOMAIN']['hirelines']
        # Adding candidate at acert via api
        endpoint = '/api/hirelines-send-candidate-schedule-link'

        schedule_link_endpoint = f'/candidate-schedule-interview/{enc_candidate_id}/'
        schedule_link_url = urljoin(hirelines_domain, schedule_link_endpoint)

        url = urljoin(acert_domain, endpoint)
        print("url",url)

        candidate_data = {
            'firstname' : candidate_details.firstname,
            'lastname' : candidate_details.lastname,
            'email': candidate_details.email,
            'mobile': candidate_details.mobile,
            'company_id': candidate_details.companyid,
            'reference_id': candidate_details.candidateid,
            'job_id': candidate_details.jobid,
            'candidate_id': candidate_details.id,
            'url': schedule_link_url
        }
        if candidate_details.profileid:
                addProfileActivityDB(candidate_details.profileid,"IS","Interview Scheduling Sent",user_data.id)
        response = requests.post(url, json=candidate_data, verify=False, timeout=10)
        response.raise_for_status()
        response_json = response.json()

        if response_json.get('statusCode') == 0:
            CallSchedule.objects.filter(candidateid=candidate_id).update(status='W')

            # if candidate_details.profileid:
            #     addProfileActivityDB(candidate_details.profileid,"IS","Interview Scheduling Sent",user_data.id)
            return True

        else:
            raise Exception(response_json.get('error', 'Email sending failed'))

    except Exception as e:
        raise
    


def createProfileActivityDB(dataObjs):
    try:

        last_seq = (
            ProfileActivity.objects
            .filter(profileid=dataObjs["profileid"])
            .aggregate(max_seq=Max("sequence"))
            .get("max_seq")
        )

        next_seq = (last_seq or 0) + 1
        companyid=None
        if dataObjs["profileid"]:
            companyid= Profile.objects.get(id=dataObjs["profileid"]).companyid
        profile_activity = ProfileActivity(
            profileid = dataObjs["profileid"],
            datentime = datetime.now(),
            sequence = next_seq,
            activitycode = "PC",
            activityname = "Profile Created",
            acvityuserid = dataObjs["acvityuserid"],
            companyid= companyid
        )
        
        profile_activity.save()

    except Exception as e:
        raise


def scheduleCandidateInterviewDB(dataObjs):
    try:
       
        raw_cid = str(dataObjs.get('candidate_id'))
        # company_account = Account.objects.get(companyid=user.companyid)
        # company_credits = CompanyCredits.objects.get(companyid=user.companyid,transtype="I")
        # if company_account.balance >= company_credits.credits:
        # encrypted_cid = unquote(dataObjs.get('candidate_id'))
        # dataObjs['candidate_id'] = encrypted_cid
        # dataObjs['candidate_id'] = decrypt_code(dataObjs['candidate_id'])
        if raw_cid.isdigit():
            # If it's just numbers (e.g., "432"), use it directly
            dataObjs['candidate_id'] = raw_cid
        else:
            # If it's not a number, assume it's encrypted and decrypt it
            encrypted_cid = unquote(raw_cid)
            dataObjs['candidate_id'] = decrypt_code(encrypted_cid)
        call_details = CallSchedule.objects.filter(candidateid=dataObjs['candidate_id']).last()
        if call_details:    
            datentime_str = ' '.join(dataObjs['slot_id'].split('__')[:2])
            datentime = datetime.strptime(datentime_str, '%a-%d-%b-%Y %I_%M_%p') 
            interviewer = dataObjs['slot_id'].split('__')[2:]
            interviewer_id = interviewer[0]
            
            scheduled_check = CallSchedule.objects.filter(Q(interviewerid=interviewer_id), Q(datentime=datentime),
                                                            Q(status='S')|Q(status='R'))
            
            print("scheduled_check",scheduled_check)
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
           
                call_details.companyid = candidate.companyid
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
                    'to_emails': to_mails,
                    'instructions': call_details.instructions,
                    'schedule_type':dataObjs['schedule_type']
                }

                acert_domain = getConfig()['DOMAIN']['acert']
                endpoint = '/api/schedule-interview'

                url = urljoin(acert_domain, endpoint)

                send_interview_data = requests.post(url, json=interview_data)

                if candidate.profileid:
                    addProfileActivityDB(candidate.profileid,"SCH","Interview Scheduled")

                return "Slot Booked"
            else: 
                return "Please select another slot"
        else:
            return "No Candidate"
        # else:
        #     return "insufficient_credits"
    except Exception as e:
        print(str(e))
        raise


def jdRecruiterAssignDB(dataObjs):
    try:

        recruiter_ids_str = ",".join(map(str, dataObjs["recruiter_ids"]))

        jd = JobDesc.objects.get(id=dataObjs["jdid"])
        jd.recruiterids = recruiter_ids_str
        jd.save()
        
    except Exception as e:
        raise


def updateProfileScoreDB(profile_id):
    try:
        from app_api.functions.profile_strength import CalculateProfileScoring
        
        profileScore = CalculateProfileScoring()
        profile_strength = profileScore.score_profile(profile_id)
        profile = Profile.objects.get(id=profile_id)
        profile.strength = profile_strength["percentage"]
        profile.educationscore = profile_strength["breakdown"]["education"]["percentage"]
        profile.experiencescore = profile_strength["breakdown"]["experience"]["percentage"]
        profile.projectsscore = profile_strength["breakdown"]["projects"]["percentage"]
        profile.skillsscore = profile_strength["breakdown"]["skills"]["percentage"]
        profile.certificatesscore = profile_strength["breakdown"]["certificates"]["percentage"]
        profile.awardsscore = profile_strength["breakdown"]["awards"]["percentage"]
        profile.save()
        
    except Exception as e:
        raise


@transaction.atomic
def updateFullProfileDB(data):

    def to_int(val):
        try:
            if val in ("", None):
                return None
            return int(val)
        except:
            return None

    def safe_str(val):
        return val if val not in ("", None) else None

    profile_id = data.get("profileid")
    if not profile_id:
        raise Exception("profileid missing")

    profile = Profile.objects.get(id=profile_id)
    updateProfileScoreDB(profile_id)
    profile_block = data.get("profile", {})
    personal = profile_block.get("personal", {})

    # -------- PROFILE (PERSONAL + ADDRESS) --------
    profile.title = safe_str(personal.get("title"))
    profile.firstname = safe_str(personal.get("firstname"))
    profile.middlename = safe_str(personal.get("middlename"))
    profile.lastname = safe_str(personal.get("lastname"))
    profile.email = safe_str(personal.get("email"))
    profile.mobile = safe_str(personal.get("mobile"))
    profile.linkedin = safe_str(personal.get("linkedin"))
    profile.facebook = safe_str(personal.get("facebook"))
    profile.passportnum = safe_str(personal.get("passportnum"))
    profile.fathername = safe_str(personal.get("fathername"))
    profile.nativeof = safe_str(personal.get("nativeof"))

    dob = personal.get("dateofbirth")
    profile.dateofbirth = (
        datetime.strptime(dob, "%Y-%m-%d").date() if dob else None
    )

    profile.save()

    address_data = personal.get("address", {})
    address, _ = ProfileAddress.objects.get_or_create(profileid=profile_id)

    address.addline1 = safe_str(address_data.get("addline1"))
    address.addline2 = safe_str(address_data.get("addline2"))
    address.city     = safe_str(address_data.get("city"))
    address.state    = safe_str(address_data.get("state"))
    address.country  = safe_str(address_data.get("country"))
    address.zipcode  = safe_str(address_data.get("zipcode"))

    address.save()

    # -------- EDUCATION --------
    ProfileEducation.objects.filter(profileid=profile_id).delete()
    for edu in profile_block.get("education", []):
        ProfileEducation.objects.create(
            profileid=profile_id,
            sequence=to_int(edu.get("sequence")),
            course=safe_str(edu.get("course")),
            institute=safe_str(edu.get("institute")),
            yearfrom=to_int(edu.get("yearfrom")),
            yearto=to_int(edu.get("yearto")),
            grade=safe_str(edu.get("grade")),
        )

    # -------- EXPERIENCE --------
    ProfileExperience.objects.filter(profileid=profile_id).delete()
    for exp in profile_block.get("experience", []):
        ProfileExperience.objects.create(
            profileid=profile_id,
            sequence=to_int(exp.get("sequence")),
            jobtitle=safe_str(exp.get("jobtitle")),
            company=safe_str(exp.get("company")),
            yearfrom=to_int(exp.get("yearfrom")),
            yearto=to_int(exp.get("yearto")),
        )

    # -------- SKILLS --------
    skills_data = profile_block.get("skills", {})
    skills, _ = ProfileSkills.objects.get_or_create(profileid=profile_id)
    skills.primaryskills = safe_str(skills_data.get("primaryskills"))
    skills.secondaryskills = safe_str(skills_data.get("secondaryskills"))
    skills.save()

    # -------- PROJECTS --------
    ProfileProjects.objects.filter(profileid=profile_id).delete()
    for proj in profile_block.get("projects", []):
        ProfileProjects.objects.create(
            profileid=profile_id,
            sequence=to_int(proj.get("sequence")),
            projectname=safe_str(proj.get("projectname")),
            clientname=safe_str(proj.get("clientname")),
            roleplayed=safe_str(proj.get("roleplayed")),
            skillsused=safe_str(proj.get("skillsused")),
            yearsfrom=to_int(proj.get("yearsfrom")),
            yearsto=to_int(proj.get("yearsto")),
        )

    # -------- AWARDS --------
    ProfileAwards.objects.filter(profileid=profile_id).delete()
    for a in profile_block.get("awards", []):
        ProfileAwards.objects.create(
            profileid=profile_id,
            sequence=to_int(a.get("sequence")),
            awardname=safe_str(a.get("awardname")),
            year=to_int(a.get("year")),
        )

    # -------- CERTIFICATES --------
    ProfileCertificates.objects.filter(profileid=profile_id).delete()
    for c in profile_block.get("certificates", []):
        ProfileCertificates.objects.create(
            profileid=profile_id,
            sequence=to_int(c.get("sequence")),
            certname=safe_str(c.get("certname")),
            year=to_int(c.get("year")),
        )


def addWorkspaceDB(dataObjs,user_data):
    try:

        workspace = Workspace(
            clientid = dataObjs["client"],
            project = dataObjs["project"],
            startdate = dataObjs["startdate"],
            notes = dataObjs["notes"],
            jd_ids = dataObjs["jd_ids"],
            createdby = user_data.id,
            createdat = datetime.now(),
            status = "A"
        )

        workspace.save()
        
    except Exception as e:
        raise


def addProfileActivityDB(profileid,activity_code,activityname,userid=None):
    try:
        last_seq = (
            ProfileActivity.objects
            .filter(profileid=profileid)
            .aggregate(max_seq=Max("sequence"))
            .get("max_seq")
        )

        next_seq = (last_seq or 0) + 1
        companyid=None
        if profileid:
            companyid= Profile.objects.get(id=profileid).companyid
        profile_activity = ProfileActivity(
            profileid = profileid,
            datentime = datetime.now(),
            sequence = next_seq,
            activitycode = activity_code,
            activityname = activityname,
            acvityuserid = userid,
            companyid=companyid,
        )

        profile_activity.save()

    except Exception as e:
        raise


def updateWorkspaceDB(dataObjs):
    try:

        workspace = Workspace.objects.get(id=dataObjs["workspaceid"])

        workspace.clientid = dataObjs["client"]
        workspace.project = dataObjs["project"]
        workspace.startdate = dataObjs["startdate"]
        workspace.notes = dataObjs["notes"]
        workspace.jd_ids = dataObjs["jd_ids"]

        workspace.save()
        
    except Exception as e:
        raise