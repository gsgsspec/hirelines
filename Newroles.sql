UPDATE hirelines.rolespermissions SET `enable` = 'HR-Admin, HR-Executive' WHERE (`id` = '1');
UPDATE hirelines.rolespermissions SET `enable` = 'HR-Admin, HR-Executive' WHERE (`id` = '3');
UPDATE hirelines.rolespermissions SET `enable` = 'HR-Admin, HR-Executive' WHERE (`id` = '5');
UPDATE hirelines.rolespermissions SET `enable` = 'HR-Admin, HR-Executive' WHERE (`id` = '8');
UPDATE hirelines.rolespermissions SET `enable` = 'HR-Admin, HR-Executive' WHERE (`id` = '11');

UPDATE hirelines.rolespermissions SET `enable` = 'Interviewer, HR-Admin, HR-Executive' WHERE (`id` = '4');
UPDATE hirelines.rolespermissions SET `enable` = 'Interviewer, HR-Admin, HR-Executive' WHERE (`id` = '6');

UPDATE hirelines.rolespermissions SET `function_icon` = 'fas fa-video' WHERE (`id` = '4');





/*
-- Query: SELECT * FROM hirelines.rolespermissions
LIMIT 0, 50000

-- Date: 2024-12-02 16:38
*/
INSERT INTO hirelines.rolespermissions (`id`,`function`,`sub_function`,`function_category`,`function_link`,`enable`,`function_icon`,`orderby`) VALUES (1,'Dashboard',NULL,'Dashboard','dashboard','HR-Admin, HR-Executive','fas fa-chart-line',1);
INSERT INTO hirelines.rolespermissions (`id`,`function`,`sub_function`,`function_category`,`function_link`,`enable`,`function_icon`,`orderby`) VALUES (2,'Job Descriptions',NULL,'Job Descriptions','job-descriptions','HR-Admin, HR-Executive','fas fa-file-alt',2);
INSERT INTO hirelines.rolespermissions (`id`,`function`,`sub_function`,`function_category`,`function_link`,`enable`,`function_icon`,`orderby`) VALUES (3,'Interview Candidates',NULL,'Interview Candidates','interviews','Interviewer, HR-Admin, HR-Executive','fas fa-video',4);
INSERT INTO hirelines.rolespermissions (`id`,`function`,`sub_function`,`function_category`,`function_link`,`enable`,`function_icon`,`orderby`) VALUES (4,'Candidates',NULL,'Candidates','candidates','HR-Admin, HR-Executive','fas fa-users',3);
INSERT INTO hirelines.rolespermissions (`id`,`function`,`sub_function`,`function_category`,`function_link`,`enable`,`function_icon`,`orderby`) VALUES (5,'Feedback',NULL,'Feedback','feedbacks','Interviewer, HR-Admin, HR-Executive','fas fa-comment-dots',6);
INSERT INTO hirelines.rolespermissions (`id`,`function`,`sub_function`,`function_category`,`function_link`,`enable`,`function_icon`,`orderby`) VALUES (6,'Email Templates',NULL,'Email Templates','email-templates','HR-Admin','fas fa-envelope',9);
INSERT INTO hirelines.rolespermissions (`id`,`function`,`sub_function`,`function_category`,`function_link`,`enable`,`function_icon`,`orderby`) VALUES (7,'Evaluation',NULL,'Evaluation','evaluation','HR-Admin, HR-Executive','fas fa-tasks',5);
INSERT INTO hirelines.rolespermissions (`id`,`function`,`sub_function`,`function_category`,`function_link`,`enable`,`function_icon`,`orderby`) VALUES (8,'Branding',NULL,'Branding','branding','HR-Admin','fas fa-palette',8);
INSERT INTO hirelines.rolespermissions (`id`,`function`,`sub_function`,`function_category`,`function_link`,`enable`,`function_icon`,`orderby`) VALUES (9,'Users',NULL,'Users','users','HR-Admin','fas fa-user',10);
INSERT INTO hirelines.rolespermissions (`id`,`function`,`sub_function`,`function_category`,`function_link`,`enable`,`function_icon`,`orderby`) VALUES (10,'Reports',NULL,'Reports','reports','HR-Admin, HR-Executive','fas fa-file',11);
INSERT INTO hirelines.rolespermissions (`id`,`function`,`sub_function`,`function_category`,`function_link`,`enable`,`function_icon`,`orderby`) VALUES (11,'Company',NULL,'Company','company-data','HR-Admin','fas fa-building',7);
