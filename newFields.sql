ALTER TABLE hirelines.jobdesc 
ADD COLUMN jdlibraryid INT NULL AFTER id;

ALTER TABLE `hirelines`.`jobdesc` 
CHANGE COLUMN `title` `title` VARCHAR(300) NULL DEFAULT NULL ;
