function testRequirements(testType){

    var testName
    if (testType == 'screening'){
        testName = 'Screening'
    }
    else if(testType == 'coding'){
        testName = 'Coding'
    }
    else if(testType == 'interview'){
        testName = 'Interview'
    }

    if(testName){
        document.getElementById('modalCenterTitle').innerText = testName
        document.getElementById('testType').dataset['test_type'] = testName
    }

}


function addTest(){
    var promotValue = document.getElementById('promot_level').value;
    var testName = document.getElementById('testType').value;
    var testNameValidator = document.getElementById('test_name_validator');
    var promotValidator = document.getElementById('promot_validator');
    var saveTest = true;

    // Check test name validation
    if (!testName) {
        testNameValidator.hidden = false;  // Show the validation message
        saveTest = false
    } else {
        testNameValidator.hidden = true;   // Hide the validation message
    }

    // Check promotion level validation
    if (!promotValue) {
        promotValidator.hidden = false;    // Show the validation message
        saveTest = false
    } else {
        promotValidator.hidden = true;     // Hide the validation message
    }

    if(saveTest){
        $.post(CONFIG['portal'] + "/api/jd-add-test", final_data, function (res) {
        
            if (res.statusCode == 0){
                if (res.token == 'token_generated'){
                    // window.location.href = '/courses';
                    if(res.data == 'HR'){
                        window.location.href = '/dashboard'
                    }
                }
                else{
                    $('#invalid_cred').removeAttr('hidden');
                }
            }

        })
    }
}




function addInterviewer(){

}