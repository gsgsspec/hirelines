var perviousLibrary
var perviousSelectedTest = null
var screeningBackgroundColor = '#efebfd'
var codingBackgroundColor = '#defaeb'
var interviewBackgroundColor = '#e2ebfd'
var screenMainColor = '#8763ee'
var codingMainColor = '#00d462'
var interviewMainColor = '#1f68f3'
var testsList = []

function getPapersLibrarys(){
    
    var jdlib = parseInt(jdlibraryid)
    var final_data = {
        "data":JSON.stringify(jdlib),
        csrfmiddlewaretoken: CSRF_TOKEN,
    };

    $.post(CONFIG['acert'] + "/api/libraryPaper-Names", final_data, function (res) {
        
        if (res.statusCode == 0){
            if(res.data){
                AppendSectionsAndQuestions(res.data)
            }
        }

    })

}

getPapersLibrarys()



function workFlowData(){
    
    var jdlib = parseInt(jdId)
    var final_data = {
        "data":JSON.stringify(jdlib),
        csrfmiddlewaretoken: CSRF_TOKEN,
    };

    $.post(CONFIG['portal'] + "/api/work-flow-data", final_data, function (res) {
        
        if (res.statusCode == 0){
            if(res.data){
                createTest(res.data,'edit')
            }
        }

    })

}

workFlowData()

function createTest(data){
    //  create cards by calling this function 
    for(var test = 0; test < data.length; test++){
        addTestCardToShow(data[test]['papertitle'], 60,data[test]['papertype'],data[test])  
        var key_ = data[test]['id']
        var tests = {[key_]: data[test]}
        testsList.push(tests)
    }
}



function AppendSectionsAndQuestions(data) {
    document.getElementById('selectedLibrary').innerText = data[0]['title'];
    
    var LibraryQuestionsList

    for (var lib = 0; lib < data.length; lib++) {

        var libraryTitlesContainer = document.getElementById('sectionTitlesContainer');
            libraryTitlesContainer.insertAdjacentHTML('beforeend','<div class="py-2 px-2 my-2 mx-3 cust_cursor library_seprator custm_margin_to_selected_library" id="library_' +  data[lib]['id'] + '" onclick="showLibrary(this.id,' +  data[lib]['id'] + ')">' + data[lib]['title'] + '</div>');

        LibraryQuestionsList = data[lib]['questionsList'];

        if (LibraryQuestionsList.length > 0) {

            var questionLibraryContainer = document.createElement('div');
            questionLibraryContainer.id = 'Questions_Library_' + data[lib]['id'];

            for (var ques = 0; ques < LibraryQuestionsList.length; ques++) {
                
                // Create question container
                var questionContainer = document.createElement('div');
                questionContainer.classList.add('each_question_container', 'my-2');

                var questionText = document.createElement('div');
                // Clean the question text by:
                // 1. Replacing \u sequences (like \u0021) with an empty string.
                // 2. Replacing multiple spaces or new lines (\r \n \t) with a single space.
                var cleanedQuestion = LibraryQuestionsList[ques].question
                .replace(/\\u[0-9A-Fa-f]{4}/g, '')   // Removes \uXXXX sequences.
                .replace(/\s+/g, ' ');                // Replaces multiple spaces/new lines with a single space.

                questionText.innerText = (ques + 1) + ' . ' + cleanedQuestion;

                // Create checkbox container
                var questionCheckBoxContainer = document.createElement('div');
                var questionCheckBox = document.createElement('input');
                questionCheckBox.type = 'checkbox';
                questionCheckBox.classList.add('form-check-input');
                questionCheckBox.checked = true;

                // Append checkbox and question text to container
                questionCheckBoxContainer.append(questionCheckBox);
                questionContainer.append(questionText);
                questionContainer.append(questionCheckBoxContainer);

                // Append the questionContainer to questionLibraryContainer
                questionLibraryContainer.append(questionContainer);

                var questionSeprator = document.createElement('hr')
                // questionSeprator.style.height = '0.5px !important;'
                questionSeprator.classList.add('hrElement')
                questionSeprator.style.borderColor = '#dbdbe1 !important;'
                questionLibraryContainer.append(questionSeprator);
            }

            if(lib == 0){ // instial we select first library & we show first library question
                document.getElementById('library_'+data[lib]['id']).classList.add('active_selected_library')
                perviousLibrary = data[lib]['id']
            }
            else{ // hidde questions containers except first questions container instial
                questionLibraryContainer.hidden = true 
            }

            // Append the question library container after all questions are added
            document.getElementById('question_container_vertical_scroll').append(questionLibraryContainer);
        }
    }
}


function showLibrary(element,libraryId){

    if(libraryId != perviousLibrary){

        // library select active inactive 
        // active
        var addSeclectedClass = document.getElementById('library_'+libraryId)
        addSeclectedClass.classList.add('active_selected_library')

        // change the Library name on top of Questions Container
        document.getElementById('selectedLibrary').innerText = addSeclectedClass.innerText

        // Inactive
        var addSeclectedClass = document.getElementById('library_'+perviousLibrary)
        addSeclectedClass.classList.remove('active_selected_library')
        
        // Library questions Container hidde and un hidde
        // un hidde
        var showLib = document.getElementById('Questions_Library_'+libraryId)
        showLib.hidden = false

        // hidde
        var hiddeLibrary = document.getElementById('Questions_Library_'+perviousLibrary)
        hiddeLibrary.hidden = true

        perviousLibrary = libraryId
    }

}


function testRequirements(testType){

    // Hidding validators
    document.getElementById('test_name_validator').hidden = true 
    document.getElementById('promot_validator').hidden  = true

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
        document.getElementById('testType').value = testName
        document.getElementById('promot_level').value = 60
        document.getElementById('testType').dataset['test_type'] = testName
    }

}

// this function send hr selected test to backend
function addTest(){

    var testName = document.getElementById('testType').value;
    var promotValue = document.getElementById('promot_level').value;
    var testNameValidator = document.getElementById('test_name_validator');
    var promotValidator = document.getElementById('promot_validator');
    var testType = document.getElementById('testType').dataset.test_type
    var saveTest = true;

    // Check test name value validation
    if (!testName) {
        testNameValidator.hidden = false;  // Show the validation message
        saveTest = false
    } else {
        testNameValidator.hidden = true;   // Hide the validation message
    }

    // Check promotion level value validation
    if (!promotValue) {
        promotValidator.hidden = false;    // Show the validation message
        saveTest = false
    } else {
        promotValidator.hidden = true;     // Hide the validation message
    }

    if(saveTest){
        
        $('#modalCenter').modal('hide')

        dataObj = {
            'testName'        : testName,
            'promotPercentage': promotValue,
            'testType'        : testType,
            'jdId'            : jdId
        }

        var final_data = {
            'data': JSON.stringify(dataObj),
            csrfmiddlewaretoken: CSRF_TOKEN,
        }

        $.post(CONFIG['portal'] + "/api/jd-add-test", final_data, function (res) {
        
            if (res.statusCode == 0){
                if(res.data){

                    var data = res.data
                    testType = testType
                    addTestCardToShow(testName,promotValue,testType,data[0])

                    var key_ = data[0]['id']
                    addTestTolst = { [key_] : data[0]}
                    testsList.push(addTestTolst)

                    console.log('testsList :: ',testsList);

                }
            }

        })

    }
}


function addTestCardToShow(testName, promotValue,testType,data) {
    
    var testCardsContainer = document.getElementById('testCards');
    var testTypeColor
    var testTitle
    var testIcon

    if(testType == 'S' || testType == 'Screening' ){
        testTypeColor = screeningBackgroundColor
        testTitle = 'Screening'
        testIcon = '<i class="fas fa-clipboard-check" style="margin-right:5px;color:'+screenMainColor+';"></i>'
    }
    else if(testType == 'C' || testType == 'Coding'){
        testTypeColor = codingBackgroundColor
        testTitle = 'Coding'
        testIcon = '<i class="fas fa-code" style="margin-right:5px;color:'+codingMainColor+';"></i>'
    }
    else if(testType == 'I' || testType == 'Interview'){
        testTypeColor = interviewBackgroundColor
        testTitle = 'Interview'
        testIcon = '<i class="fas fa-chalkboard-teacher" style="margin-right:5px;color:'+interviewMainColor+';"></i>'
    }

    testCardsContainer.insertAdjacentHTML('beforeend',
        '<div class="col-sm-6 col-lg-4 mb-4">' +
            '<div class="card p-3 cust_cursor" style="background-color:'+testTypeColor+';" onclick="selectTest(this.id)" id="'+testTitle+'_'+data['id']+'">' +
                '<figure class="p-3 mb-0">' +
                    '<blockquote class="blockquote">' +
                        '<div>'+
                            '<figcaption class="custm_blockquote-footer mb-0 text-muted" style="display:flex;justify-content: space-between;width: 100%; color: var(--primary-color) !important; font-weight: 600;">' +
                                '<div>'+
                                    '<span id="testTypeTitle">'+ testName +'</span> &nbsp; '+testIcon+'' +
                                    '<p class="add-test-name-cust">'+testTitle+'( Promoted Value '+ promotValue +' )' +'</p>' +
                                '</div>'+
                                '<div> <i class="bx bx-edit custm-edit-icon" onclick="updateTest(event)"></i> </div>'  +
                            '</figcaption>' +
                        '</div>'+
                    '</blockquote>' +
                '</figure>' +
            '</div>' +
        '</div>'
    );
    
}


function selectTest(element_id){

    if (element_id != perviousSelectedTest){

        var test_type = element_id.split('_')[0]
        var borderClr
    
        if(test_type == 'Screening'){
            borderClr = screenMainColor
        }
        if(test_type == 'Coding'){
            borderClr = codingMainColor
        }
        if(test_type == 'Interview'){
            borderClr = interviewMainColor
        }
        
        var testBox = document.getElementById(element_id)
        testBox.style.border = '1px solid ' + borderClr
        testBox.style.boxShadow = '0 2px 6px 0 rgba(79, 80, 82, 0.56)';

        if (perviousSelectedTest){
            var testBox = document.getElementById(perviousSelectedTest)
            testBox.style.border = ''
            testBox.style.boxShadow = '0 2px 6px 0 rgba(67, 89, 113, 0.12)';
        }
        
    }
    
    perviousSelectedTest = element_id

}


function updateTest(event){
    event.stopPropagation();
    $('#modalCenter').modal('show')
}


console.log('testsList :: ',testsList);