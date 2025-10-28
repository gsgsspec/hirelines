-- SET @company_id = 1;


DELETE FROM ivfeedback
WHERE candidateid IN (SELECT id FROM candidate WHERE jobid IN (SELECT id FROM jobdesc WHERE companyid = @company_id));

DELETE FROM interviewmedia
WHERE candidateid IN (SELECT id FROM candidate WHERE jobid IN (SELECT id FROM jobdesc WHERE companyid = @company_id));

DELETE FROM callschedule
WHERE candidateid IN (SELECT id FROM candidate WHERE jobid IN (SELECT id FROM jobdesc WHERE companyid = @company_id));

DELETE FROM qresponse
WHERE candidateid IN (SELECT id FROM candidate WHERE jobid IN (SELECT id FROM jobdesc WHERE companyid = @company_id));

DELETE FROM registration
WHERE jobid IN (SELECT id FROM jobdesc WHERE companyid = @company_id);

DELETE FROM candidate
WHERE jobid IN (SELECT id FROM jobdesc WHERE companyid = @company_id);

DELETE FROM jdanalysis
WHERE jobid IN (SELECT id FROM jobdesc WHERE companyid = @company_id);

DELETE FROM brules
WHERE jobdescid IN (SELECT id FROM jobdesc WHERE companyid = @company_id);

DELETE FROM workflow
WHERE jobid IN (SELECT id FROM jobdesc WHERE companyid = @company_id);

DELETE FROM jobdesc
WHERE companyid = @company_id;

DELETE FROM credits
WHERE  companyid = @company_id;




