CREATE TABLE resume (
    id INT AUTO_INCREMENT PRIMARY KEY,
    sourceid INT NULL,
    filename VARCHAR(100) NULL,
    mailid VARCHAR(200) NULL,
    datentime DATETIME DEFAULT CURRENT_TIMESTAMP,
    companyid INT NULL,
    status CHAR(1) NULL
);

CREATE TABLE resumefile (
    id INT AUTO_INCREMENT PRIMARY KEY,
    resumeid INT NULL,
    filename VARCHAR(100) NULL,
    filecontent LONGBLOB NULL
);

CREATE TABLE profile (
    id INT AUTO_INCREMENT PRIMARY KEY,
    sourceid INT NULL,
    resumeid INT NULL,
    companyid INT NULL,
    dateofcreation DATETIME NULL,
    title VARCHAR(100) NULL,
    firstname VARCHAR(100) NULL,
    middlename VARCHAR(40) NULL,
    lastname VARCHAR(100) NULL,
    email VARCHAR(100) NULL,
    mobile VARCHAR(15) NULL,
    linkedin VARCHAR(100) NULL,
    facebook VARCHAR(100) NULL,
    passportnum VARCHAR(40) NULL,
    dateofbirth DATETIME NULL,
    fathername VARCHAR(100) NULL,
    nativeof VARCHAR(100) NULL,
    status CHAR(1) NULL,
    strength INT NULL
);

CREATE TABLE profileeducation (
    id INT AUTO_INCREMENT PRIMARY KEY,
    profileid INT NULL,
    sequence INT NULL,
    course VARCHAR(100) NULL,
    institute VARCHAR(100) NULL,
    yearfrom INT NULL,
    yearto INT NULL,
    grade VARCHAR(100) NULL
);

CREATE TABLE profileexperience (
    id INT AUTO_INCREMENT PRIMARY KEY,
    profileid INT NULL,
    sequence INT NULL,
    jobtitle VARCHAR(100) NULL,
    company VARCHAR(100) NULL,
    yearfrom INT NULL,
    yearto INT NULL
);

CREATE TABLE profileskills (
    id INT AUTO_INCREMENT PRIMARY KEY,
    profileid INT NULL,
    primaryskills VARCHAR(256) NULL,
    secondaryskills VARCHAR(256) NULL
);

CREATE TABLE profileprojects (
    id INT AUTO_INCREMENT PRIMARY KEY,
    profileid INT NULL,
    sequence INT NULL,
    projectname VARCHAR(100) NULL,
    clientname VARCHAR(100) NULL,
    roleplayed VARCHAR(100) NULL,
    skillsused VARCHAR(100) NULL,
    yearsfrom INT NULL,
    yearsto INT NULL
);

CREATE TABLE profileactivity (
    id INT AUTO_INCREMENT PRIMARY KEY,
    profileid INT NULL,
    datentime DATETIME NULL,
    sequence INT NULL,
    activitycode VARCHAR(2) NULL,
    acvityuserid INT NULL,
    activityname VARCHAR(100) NULL,
    activityremarks VARCHAR(200) NULL,
    activitystatus VARCHAR(100) NULL
);

CREATE TABLE profileawards (
    id INT AUTO_INCREMENT PRIMARY KEY,
    profileid INT NULL,
    sequence INT NULL,
    awardname VARCHAR(100) NULL,
    year INT NULL
);

CREATE TABLE profilecertificates (
    id INT AUTO_INCREMENT PRIMARY KEY,
    profileid INT NULL,
    certname VARCHAR(100) NULL,
    sequence INT NULL,
    year INT NULL
);

CREATE TABLE profileaddress (
    id INT AUTO_INCREMENT PRIMARY KEY,
    profileid INT NULL,
    addline1 VARCHAR(100) NULL,
    addline2 VARCHAR(100) NULL,
    city VARCHAR(100) NULL,
    state VARCHAR(40) NULL,
    country VARCHAR(40) NULL,
    zipcode VARCHAR(20) NULL
);


ALTER TABLE workcal CHANGE workhours hours VARCHAR(4) NULL;
ALTER TABLE workcal CHANGE empid userid INT NULL;
ALTER TABLE `workcal` 
CHANGE COLUMN `startday` `startday` VARCHAR(10) NULL DEFAULT NULL ,
CHANGE COLUMN `weekoff1` `weekoff1` VARCHAR(10) NULL DEFAULT NULL ,
CHANGE COLUMN `weekoff2` `weekoff2` VARCHAR(10) NULL DEFAULT NULL ;

INSERT INTO `role` (`Name`, `status`) VALUES ('Recruiter', 'A');
INSERT INTO `rolespermissions` (`function`, `function_category`, `function_link`, `enable`, `function_icon`, `orderby`) VALUES ('Resume Inbox', 'Resume Inbox', 'resume-inbox', 'HR-Admin, Recruiter', 'fas fa-envelope', '3');
INSERT INTO `rolespermissions` (`function`, `function_category`, `function_link`, `enable`, `function_icon`, `orderby`) VALUES ('Profile', 'Profiles', 'profiles', 'HR-Admin, Recruiter', 'fas fa-users', '5');
INSERT INTO `rolespermissions` (`function`, `function_category`, `function_link`, `enable`, `function_icon`, `orderby`) VALUES ('Work Calender', 'Work Calender', 'work-calender', 'Interviewer', 'fas fa-calendar-day', '12');