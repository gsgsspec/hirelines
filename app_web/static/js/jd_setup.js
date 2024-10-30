var perviousLibrary
var perviousTestLibrary
var perviousSelectedTest = null
var screeningBackgroundColor = '#efebfd'
var codingBackgroundColor = '#defaeb'
var interviewBackgroundColor = '#e2ebfd'
var screenMainColor = '#8763ee'
var codingMainColor = '#00d462'
var interviewMainColor = '#1f68f3'
var testsList = {}
var testCreateOrUpdate // store "create" or "update", if it create, it create a new test or update , it update the existing test 
var cureentTestId
var instialSelectTest = []
var instialLibrarySelection = {}
var testsList_ = []
var TestWithLibrariesAndQuestions = {}

$(document).ready(function () {
    
    workFlowData();
})


// get all tests list with this api
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


//  create cards by calling this function 
function createTest(data){
    for(var test = 0; test < data.length; test++){
        addTestCardToShow(data[test]['papertitle'], data[test]['promot'],data[test]['papertype'],data[test])  
        
        var key_ = data[test]['id']
        testsList[[key_]] =  data[test]
        testsList_.push(key_)

    }
    createWorkFlowContainer(data)
}

// create a container that holds libraries container and Select paper container
function createWorkFlowContainer(data){
    
    var mainContainer = document.getElementById('librarysMainContainer')

    if(data.length > 0){

        for(var container = 0; container < data.length; container++){

            var workFlowContainer = document.createElement('div')
            workFlowContainer.id = 'workFlowContainer_'+data[container]['id']
            workFlowContainer.hidden = true
            mainContainer.append(workFlowContainer)

        }

    }

}


// function AppendSectionsAndQuestions(data,workFlowId) {

//     document.getElementById('selectedLibrary').innerText = data[0]['title'];
    
//     var LibraryQuestionsList

//     for (var lib = 0; lib < data.length; lib++) {

//         LibraryQuestionsList = data[lib]['questionsList'];

//         if (LibraryQuestionsList.length > 0) {

//             var subLibraryContainer = document.createElement('div')

//             subLibraryContainer.classList.add('py-3', 'library_sub_container')

//             var libraryTitlesContainer = document.getElementById('sectionTitlesContainer');
//             libraryTitlesContainer.insertAdjacentHTML('beforeend','<div class="py-2 px-2 my-2 mx-3 cust_cursor library_seprator custm_margin_to_selected_library" id="library_' +  data[lib]['id'] + '" onclick="selectLibrary(this.id,' +  data[lib]['id'] + ')">' + data[lib]['title'] + '</div>');

//             var questionLibraryContainer = document.createElement('div');
//             questionLibraryContainer.id = 'Questions_Library_' + data[lib]['id'];

//             for (var ques = 0; ques < LibraryQuestionsList.length; ques++) {
                
//                 // Create question container
//                 var questionContainer = document.createElement('div');
//                 questionContainer.classList.add('each_question_container', 'my-2');

//                 var questionText = document.createElement('div');
//                 // Clean the question text by:
//                 // 1. Replacing \u sequences (like \u0021) with an empty string.
//                 // 2. Replacing multiple spaces or new lines (\r \n \t) with a single space.
//                 var cleanedQuestion = LibraryQuestionsList[ques].question
//                 .replace(/\\u[0-9A-Fa-f]{4}/g, '')   // Removes \uXXXX sequences.
//                 .replace(/\s+/g, ' ');                // Replaces multiple spaces/new lines with a single space.

//                 questionText.innerText = (ques + 1) + ' . ' + cleanedQuestion;

//                 // Create checkbox container
//                 var questionCheckBoxContainer = document.createElement('div');
//                 var questionCheckBox = document.createElement('input');
//                 questionCheckBox.type = 'checkbox';
//                 questionCheckBox.classList.add('form-check-input');
//                 questionCheckBox.checked = true;

//                 // Append checkbox and question text to container
//                 questionCheckBoxContainer.append(questionCheckBox);
//                 questionContainer.append(questionText);
//                 questionContainer.append(questionCheckBoxContainer);

//                 // Append the questionContainer to questionLibraryContainer
//                 questionLibraryContainer.append(questionContainer);

//                 var questionSeprator = document.createElement('hr')
//                 // questionSeprator.style.height = '0.5px !important;'
//                 questionSeprator.classList.add('hrElement')
//                 questionSeprator.style.borderColor = '#dbdbe1 !important;'
//                 questionLibraryContainer.append(questionSeprator);
//             }

//             // instial we select first library & we show first library question
//             if(lib == 0){
//                 document.getElementById('library_'+data[lib]['id']).classList.add('active_selected_library')
//                 perviousLibrary = data[lib]['id']
//             }
//             else{ // hidde questions containers except first questions container instial
//                 questionLibraryContainer.hidden = true 
//             }

//             // Append the question library container after all questions are added
//             document.getElementById('question_container_vertical_scroll').append(questionLibraryContainer);
//         }

//     }
// }


function AppendSectionsAndQuestions(data, TestCardId) {
    
    TestWithLibrariesAndQuestions[TestCardId] = data

    var subLibraryConttainer = document.createElement('div');
    subLibraryConttainer.id = 'library_sub_container_' + TestCardId;
    subLibraryConttainer.classList.add('py-3', 'library_sub_container');

    var sideLibraryTitlesContainer = document.createElement('div');
    sideLibraryTitlesContainer.id = 'sectionTitlesContainer';
    sideLibraryTitlesContainer.dataset['TestCardId'] = TestCardId;
    sideLibraryTitlesContainer.classList.add('Librarys_container', 'overflow-hidden', 'ps', 'ps--active-y','libraryContainerFnd');

    var selectedLibraryQuestionsContainer = document.createElement('div')
    selectedLibraryQuestionsContainer.style.width = '100%'

    var titleUseTemplateContainer = document.createElement('div')
    titleUseTemplateContainer.classList.add('selectedLibraryTitltandUserTemplateContainer')

    var selectedLibraryTitle = document.createElement('h4')
    selectedLibraryTitle.classList.add('questions_container_selected_title')
    selectedLibraryTitle.id = 'librarySelectedTestName_'+TestCardId

    var useTemplateButton = document.createElement('button')
    useTemplateButton.classList.add('btn', 'btn-lg', 'btn-primary', 'use_template_cust_btn')
    useTemplateButton.innerText = 'Use Template'
    useTemplateButton.id = 'selectedLibrary_'+TestCardId
    useTemplateButton.dataset['libraryid'] = ''
    useTemplateButton.onclick = () => showQuestionConatainer()
    // useTemplateButton.attributes = 'onclick="useTemplate()"'

    titleUseTemplateContainer.append(selectedLibraryTitle)
    titleUseTemplateContainer.append(useTemplateButton)

    // Create container that can hold librarys questions list
    var librariesQuestionsListContainer = document.createElement('div');
    librariesQuestionsListContainer.id = 'question_container_vertical_scroll';
    librariesQuestionsListContainer.dataset['TestCardId'] = TestCardId;
    librariesQuestionsListContainer.classList.add('questions', 'container', 'Librarys_questions_container', 'questionContainerFnd', 'overflow-hidden', 'ps', 'ps--active-y');
    librariesQuestionsListContainer.style.paddingLeft = '1rem';
    librariesQuestionsListContainer.style.paddingRight = '0rem';

    // Append the containers
    subLibraryConttainer.append(sideLibraryTitlesContainer);
    // subLibraryConttainer.append(librariesQuestionsListContainer);

    selectedLibraryQuestionsContainer.append(titleUseTemplateContainer) // append 
    selectedLibraryQuestionsContainer.append(librariesQuestionsListContainer)

    subLibraryConttainer.append(selectedLibraryQuestionsContainer);

    var workFLowContainer = document.getElementById('workFlowContainer_' + TestCardId);
    workFLowContainer.append(subLibraryConttainer);

    var SelectedPaperQuestionsContainer = document.createElement('div');
    SelectedPaperQuestionsContainer.id = 'selectedLibraryQuestionsContainer_'+TestCardId
    SelectedPaperQuestionsContainer.hidden = true
    SelectedPaperQuestionsContainer.classList.add('selectedLibrary')
    workFLowContainer.append(SelectedPaperQuestionsContainer);

    var LibraryQuestionsList;
    instialLibrarySelection[TestCardId] = []

    for (var lib = 0; lib < data.length; lib++) {
        LibraryQuestionsList = data[lib]['questionsList'];
        
        instialLibrarySelection[TestCardId].push(data[lib]['id'])

        if (LibraryQuestionsList.length > 0) {
            // var libraryTitlesContainer = document.getElementById('libraryTitlesContainer_' + TestCardId);
            // libraryTitlesContainer.insertAdjacentHTML('beforeend', '<div class="py-2 px-2 my-2 mx-3 cust_cursor library_seprator custm_margin_to_selected_library" id="library_' + data[lib]['id'] + '" onclick="selectLibrary(this.id,' + data[lib]['id'] + ','+TestCardId+')">' + data[lib]['title'] + '</div>');

            var questionLibraryContainer = document.createElement('div');
            questionLibraryContainer.id = 'Questions_Library_' + data[lib]['id'];
            questionLibraryContainer.style.paddingRight = '1rem'

            for (var ques = 0; ques < LibraryQuestionsList.length; ques++) {
                // Create question container
                var questionContainer = document.createElement('div');
                questionContainer.classList.add('each_question_container', 'my-2');

                var questionText = document.createElement('div');
                var cleanedQuestion = LibraryQuestionsList[ques].question
                    .replace(/\\u[0-9A-Fa-f]{4}/g, '')   // Removes \uXXXX sequences.
                    .replace(/\s+/g, ' ');                // Replaces multiple spaces/new lines with a single space.

                questionText.innerText = (ques + 1) + ' . ' + cleanedQuestion;

                // Create checkbox container
                var questionCheckBoxContainer = document.createElement('div');
                // var questionCheckBox = document.createElement('input');
                // questionCheckBox.type = 'checkbox';
                // questionCheckBox.classList.add('form-check-input');
                // questionCheckBox.checked = true;

                // Append checkbox and question text to container
                // questionCheckBoxContainer.append(questionCheckBox);
                questionContainer.append(questionText);
                questionContainer.append(questionCheckBoxContainer);

                // Append the questionContainer to questionLibraryContainer
                questionLibraryContainer.append(questionContainer);

                var questionSeprator = document.createElement('hr');
                questionSeprator.classList.add('hrElement');
                questionSeprator.style.borderColor = '#dbdbe1 !important;';

                questionLibraryContainer.append(questionSeprator);

                // instialLibrarySelection[TestCardId].push(data[lib]['id'])
                // console.log(LibraryQuestionsList[ques]); 
            }

            // console.log('instialLibrarySelection :: ',instialLibrarySelection);

            var fndLibraryContainer = document.getElementsByClassName('libraryContainerFnd');

            for (var container_fnd = 0; container_fnd < fndLibraryContainer.length; container_fnd++) {
                var containerWorkFlowID = fndLibraryContainer[container_fnd].dataset.TestCardId;

                if (containerWorkFlowID == TestCardId) {
                    fndLibraryContainer[container_fnd].insertAdjacentHTML('beforeend', '<div class="py-2 px-2 my-2 mx-3 cust_cursor library_seprator custm_margin_to_selected_library" id="library_' + data[lib]['id'] + '_'+TestCardId+'" onclick="selectLibrary(this.id,' + data[lib]['id'] + ','+TestCardId+')">' + data[lib]['title'] + '</div>');
                }

            }

            // Initially select first library & show first library question
            if (lib == 0) {
                document.getElementById('library_' + data[lib]['id']+'_'+TestCardId).classList.add('active_selected_library');
                perviousLibrary = data[lib]['id'];
                document.getElementById('librarySelectedTestName_'+TestCardId).innerText = data[lib]['title']
                document.getElementById('selectedLibrary_'+TestCardId).dataset['libraryid'] = data[lib]['id']
                
            } else {
                // Hide questions containers except first questions container initially
                questionLibraryContainer.hidden = true;
            }

            // Append the question library container after all questions are added
            var fndQuestionsContainer = document.getElementsByClassName('questionContainerFnd');

            for (var container_fnd = 0; container_fnd < fndQuestionsContainer.length; container_fnd++) {
                var containerWorkFlowID = fndQuestionsContainer[container_fnd].dataset.TestCardId;

                if (containerWorkFlowID == TestCardId) {
                    fndQuestionsContainer[container_fnd].append(questionLibraryContainer);
                }

            }

            // **Reinitialize the scroll bar after appending**
            if (typeof PerfectScrollbar !== 'undefined') {
                new PerfectScrollbar(librariesQuestionsListContainer);
                new PerfectScrollbar(sideLibraryTitlesContainer);
            } else {
                console.warn('Perfect Scrollbar library not found!');
            }
        }
    }
    // console.log('instialLibrarySelection :: ',instialLibrarySelection);
}


// function selectLibrary(element,libraryId,SelectedTestId){

//     if(libraryId != perviousLibrary){

//         var title = document.getElementById('librarySelectedTestName_'+SelectedTestId)
//         if(title){
//             title.innerText = document.getElementById(element).innerText
//         }

//         // library select active inactive 
//         // active
//         var addSeclectedClass = document.getElementById('library_'+libraryId)
//         addSeclectedClass.classList.add('active_selected_library')

//         // Inactive
//         if((SelectedTestId == perviousTestLibrary) || (!perviousTestLibrary) || (perviousTestLibrary != SelectedTestId)){

//             var addSeclectedClass = document.getElementById('library_'+perviousLibrary)
//             if(addSeclectedClass){
//                 addSeclectedClass.classList.remove('active_selected_library')
//             }

//         }
        
//         // Library questions Container hidde and un hidde
//         // un hidde
//         var showLib = document.getElementById('Questions_Library_'+libraryId)
//         if(showLib){
//             showLib.hidden = false
//         }

//         // hidde
//         var hiddeLibrary = document.getElementById('Questions_Library_'+perviousLibrary)
//         if(hiddeLibrary){
//             hiddeLibrary.hidden = true
//         }

//         perviousLibrary = libraryId
//         perviousTestLibrary = SelectedTestId
//     }

// }


function selectLibrary(element,libraryId,SelectedTestId){

    var currentLibList = instialLibrarySelection[SelectedTestId]
    var selectLibId = document.getElementById(element)

    for(var lib = 0; lib < currentLibList.length; lib++){

        var libId = 'library_'+currentLibList[lib]+'_'+SelectedTestId

        if(selectLibId.id == libId){
            selectLibId.classList.add('active_selected_library') // active the selected library
            document.getElementById('librarySelectedTestName_'+SelectedTestId).innerText = selectLibId.innerText // change the selected library name
            document.getElementById('Questions_Library_'+currentLibList[lib]).hidden = false // showing questions container
            document.getElementById('selectedLibrary_'+SelectedTestId).dataset['libraryid'] = libraryId // put library id in use template 
        }
        else{
            var lstLib = document.getElementById(libId)
            lstLib.classList.remove('active_selected_library')
            document.getElementById('Questions_Library_'+currentLibList[lib]).hidden = true
        }

    }

    var scrollBar = document.getElementsByClassName('ps__rail-y')

    if(scrollBar.length > 0){
        for(var scroll_ = 0; scroll_ < scrollBar.length; scroll_++){
            scrollBar[scroll_].style.top = '0px'
        }
    }

}



function createNewTestModalOpen(testType){

    testCreateOrUpdate = 'create'
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
function saveOrUpdateTest(){
    
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

        if (testCreateOrUpdate == 'create'){

            dataObj = {
                'createOrUpdate'  : testCreateOrUpdate,
                'testName'        : testName,
                'promotPercentage': promotValue,
                'testType'        : testType,
                'jdId'            : jdId
            }

        }

        if (testCreateOrUpdate == 'update'){

            dataObj = {
                'createOrUpdate'  : testCreateOrUpdate,
                'testId'          : cureentTestId,
                'testName'        : testName,
                'promotPercentage': promotValue,
                'testType'        : testType,
                'jdId'            : jdId
            }

        }

        var final_data = {
            'data': JSON.stringify(dataObj),
            csrfmiddlewaretoken: CSRF_TOKEN,
        }

        $.post(CONFIG['portal'] + "/api/jd-add-or-update-test", final_data, function (res) {
        
            if (res.statusCode == 0){
                if(res.data){
                    var data = res.data

                    // test is updated and update card data
                    if ('updateEvent' in data && data['updateEvent'] == 'Y'){

                        var key_ = data['id']
                        testsList[[key_]] =  data
                        updateCardAfterSaveData(testsList,data['id'])
                    }
                    else{
                        // test is add and create card
                        
                        var key_ = data[0]['id']
                        testsList[[key_]] =  data[0]
                        testsList_.push(key_)
                        
                        testType = testType
                        addTestCardToShow(testName,promotValue,testType,data[0])

                    }

                }
            }

        })

    }
}


function updateCardAfterSaveData(allTestsList,testId){

    var testType = allTestsList[testId]['papertype']
    var testName
    if (testType == 'S'){
        testName = 'Screening'
    }
    else if(testType == 'E'){
        testName = 'Coding'
    }
    else if(testType == 'I'){
        testName = 'Interview'
    }

    document.getElementById('testTypeTitle_'+testId).innerText = allTestsList[testId]['papertitle']
    document.getElementById('testCardTestType_'+testId).innerText = ""+testName+"( Promoted Value "+allTestsList[testId]['promot']+" )"

}


function addTestCardToShow(testName, promotValue,testType,data) {
    
    var testCardsContainer = document.getElementById('testCards');
    var testTypeColor
    var testTitle
    var testIcon
    var testDesc

    if(testType == 'S' || testType == 'Screening' ){
        testTypeColor = screeningBackgroundColor
        testTitle = 'S'
        testDesc  = 'Screening'
        testIcon = '<i class="fas fa-clipboard-check" style="margin-right:12px;color:'+screenMainColor+';font-size:2rem;"></i>'
    }
    else if(testType == 'E' || testType == 'Coding'){
        testTypeColor = codingBackgroundColor
        testTitle = 'E'
        testDesc  = 'Coding'
        testIcon = '<i class="fas fa-code" style="margin-right:12px;color:'+codingMainColor+';font-size:2rem;"></i>'
    }
    else if(testType == 'I' || testType == 'Interview'){
        testTypeColor = interviewBackgroundColor
        testTitle = 'I'
        testDesc  = 'Interview'
        testIcon = '<i class="fas fa-chalkboard-teacher" style="margin-right:12px;color:'+interviewMainColor+';font-size:2rem;"></i>'
    }

    testCardsContainer.insertAdjacentHTML('beforeend',
        '<div class="col-sm-6 col-lg-4 mb-4">' +
            '<div class="card p-3 cust_cursor" style="background-color:'+testTypeColor+';" onclick="selectTest(this.id)" id="'+testTitle+'_'+data['id']+'">' +
                '<figure class="px-0 py-3 mb-0">' +
                    '<blockquote class="blockquote">' +
                        '<div>'+
                            '<figcaption class="custm_blockquote-footer mb-0 text-muted" style="display:flex;justify-content: space-between;width: 100%; color: var(--primary-color) !important; font-weight: 600;">' +
                                '<div style="display: flex; flex-direction: row;">'+
                                    ''+testIcon+''+
                                    '<div>'+
                                        '<span id="testTypeTitle_'+data['id']+'">'+ testName +'</span> &nbsp; ' +
                                        '<p class="add-test-name-cust" id="testCardTestType_'+data['id']+'">'+testDesc+'( Promoted Value '+ promotValue +' )' +'</p>' +
                                    '</div>'+
                                '</div>'+
                                '<div> <i class="bx bx-edit custm-edit-icon" id="editTestCard_'+data['id']+'" onclick="updateTest(event,'+data['id']+')"></i> </div>'  +
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
        var workFlowId = element_id.split('_')[1]

        if(element_id){

            var workFlowId = element_id.split('_')[1]
            var currentSelectedTestWorkFlow = document.getElementById('workFlowContainer_'+workFlowId)
            if(currentSelectedTestWorkFlow){
                currentSelectedTestWorkFlow.hidden = false
            }

        }

        if(perviousSelectedTest){

            var perviousSelectedTestId = perviousSelectedTest.split('_')[1]
            var perviousSelectedTestWorkFlow = document.getElementById('workFlowContainer_'+perviousSelectedTestId)
            if(perviousSelectedTestWorkFlow){
                perviousSelectedTestWorkFlow.hidden = true
            }

        }

        // it only allow get library one and create html container 
        if (!instialSelectTest.includes(workFlowId)) {
            instialSelectTest.push(workFlowId)
            getPapersLibraries(test_type, workFlowId);
        }
        
        var borderClr
        
        if(test_type == 'S'){
            borderClr = screenMainColor
        }
        if(test_type == 'E'){
            borderClr = codingMainColor
        }
        if(test_type == 'I'){
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
    document.getElementById('librarysMainContainer').hidden = false

}


function updateTest(event,currentSelectedtestId){

    testCreateOrUpdate = 'update'
    cureentTestId = currentSelectedtestId
    event.stopPropagation();
    openUpdateTestModel(currentSelectedtestId)
    
}


function openUpdateTestModel(currentSelectedtestId){

    if(currentSelectedtestId){
        var testType = testsList[currentSelectedtestId]['papertype']
        var testName
        if (testType == 'screening' || testType == 'S'){ 
            testName = 'Screening'
        }
        else if(testType == 'coding' || testType == 'E'){
            testName = 'Coding'
        }
        else if(testType == 'interview' || testType == 'I'){
            testName = 'Interview'
        }

        document.getElementById('modalCenterTitle').innerText = testName
        document.getElementById('testType').value = testsList[currentSelectedtestId]['papertitle'] // test title or test name
        document.getElementById('promot_level').value = testsList[currentSelectedtestId]['promot']
        document.getElementById('testType').dataset['test_type'] = testsList[currentSelectedtestId]['papertype']
        $('#modalCenter').modal('show')
    }
    
}


document.getElementById('script_copy_btn').addEventListener('click', function() {
    const scriptValue = document.getElementById('scriptTextarea').value;
    const functionValue = document.getElementById('functionTextarea').value;
    const combinedText = `${scriptValue}\n${functionValue}`;
    
    navigator.clipboard.writeText(combinedText).then(() => {
        const scriptTextarea = document.getElementById('scriptTextarea');
        const functionTextarea = document.getElementById('functionTextarea');

        scriptTextarea.classList.add('flash-border');
        functionTextarea.classList.add('flash-border');

        setTimeout(() => {
            scriptTextarea.classList.remove('flash-border');
            functionTextarea.classList.remove('flash-border');
        }, 500);

        console.log('Copied to clipboard!');
    }).catch(err => {
        // Optionally handle the error
        console.error('Error copying text: ', err);
    });
});


// Function to get paper libraries
function getPapersLibraries(test_type, workFlowId) {

    checkTestHasPaper(workFlowId).then(testPaperData => {

        if (testPaperData['paperId'] == 'N') { // Show libraries if no paper ID
            dataObj = {
                'jdLibId': parseInt(jdlibraryid), // Extract subject ID from JD library
                'LibType': test_type // Paper Type
            }

            var final_data = {
                'data': JSON.stringify(dataObj),
                csrfmiddlewaretoken: CSRF_TOKEN,
            };

            $.post(CONFIG['acert'] + "/api/libraryPaper-Names", final_data, function (res) {
                if (res.statusCode == 0 && res.data) {
                    AppendSectionsAndQuestions(res.data,workFlowId);
                }
            }).fail(function (error) {
                console.error("API request failed:", error);
            });

        } else {
            // Show selected paper here
        }
    }).catch(error => {
        console.error("Error checking test has paper:", error);
    });
    
}


// Refactor checkTestHasPaper to return a Promise
function checkTestHasPaper(workFlowId) {

    dataObj = {
        'workFlowId': parseInt(jdlibraryid),
    };

    var final_data = {
        'data': JSON.stringify(dataObj),
        csrfmiddlewaretoken: CSRF_TOKEN,
    };

    return new Promise((resolve, reject) => {
        $.post(CONFIG['portal'] + "/api/check-test-has-paper", final_data, function (res) {
            if (res.statusCode == 0 && res.data) {
                resolve(res.data); // Resolve the promise with res.data
            } else {
                reject("No valid data received");
            }
        }).fail(function (error) {
            console.error("API request failed:", error);
            reject(error); // Reject the promise if API fails
        });
    });
}


function showQuestionConatainer(element){
    
    for(var testCount = 0; testCount < testsList_.length; testCount++){

        var testId = testsList_[testCount]
        var testElementId = 'workFlowContainer_'+testId
        var workFLowContainer = document.getElementById(testElementId)

        if(workFLowContainer.hidden == false){
            document.getElementById('selectedLibraryQuestionsContainer_'+testId).hidden = false
            document.getElementById('library_sub_container_'+testId).hidden = true;

            createQuestionsContainer(testId)
        }

    }
    
}

function createQuestionsContainer(testId){
    var buttonData = document.getElementById('selectedLibrary_'+testId)
    var selectedLibraryId = buttonData.dataset['libraryid']
    
    var testLibraries = TestWithLibrariesAndQuestions[testId]

    for(var lib = 0; lib < testLibraries.length; lib++){

        var librariesQuestionsListContainer = document.createElement('div');
        librariesQuestionsListContainer.id = 'question_container_vertical_scroll';
        librariesQuestionsListContainer.dataset['TestCardId'] = testId;
        librariesQuestionsListContainer.classList.add('questions', 'Librarys_questions_container', 'questionContainerFnd', 'overflow-hidden', 'ps', 'ps--active-y', 'm-0','w-100');
        librariesQuestionsListContainer.style.paddingLeft = '1rem';
        librariesQuestionsListContainer.style.paddingRight = '0rem';
        librariesQuestionsListContainer.width = '100%'

        if(testLibraries[lib]['id'] == selectedLibraryId){

            var questionContainerHeader = document.createElement('div') // Heading container that container title and static questions Count Dynamic Question count
            questionContainerHeader.classList.add('question_container_header')
            
            var selectedLibraryTitle = document.createElement('h4') // selected library title
            selectedLibraryTitle.classList.add('py-2','m-0')
            selectedLibraryTitle.innerText = testLibraries[lib]['title']
            selectedLibraryTitle.style.width = 'max-content'

            var questionsCountContainer = document.createElement('div')
            questionsCountContainer.style.display = 'flex'
                var staticQuestionContainer = document.createElement('div')
                staticQuestionContainer.style.display = 'flex'
                    var staticQuestionlabel = document.createElement('div')
                    staticQuestionlabel.innerText = 'Static Questions'
                    var staticQuestionCounBox = document.createElement('div')
                    staticQuestionCounBox.innerText = '5'

                var dynQuestionContainer = document.createElement('div')
                dynQuestionContainer.style.display = 'flex'
                dynQuestionContainer.classList.add('mx-3')
                    var dynQuestionlabel = document.createElement('div')
                    dynQuestionlabel.innerText = 'Static Questions'
                    var dynQuestionCounBox = document.createElement('div')
                    dynQuestionCounBox.innerText = '12'

                staticQuestionContainer.append(staticQuestionlabel)
                staticQuestionContainer.append(staticQuestionCounBox)
                dynQuestionContainer.append(dynQuestionlabel)
                dynQuestionContainer.append(dynQuestionCounBox)

            questionsCountContainer.append(staticQuestionContainer)
            questionsCountContainer.append(dynQuestionContainer)

            questionContainerHeader.append(selectedLibraryTitle)
            questionContainerHeader.append(questionsCountContainer)

            var questionsContainer = document.getElementById('selectedLibraryQuestionsContainer_'+testId)
            questionsContainer.append(questionContainerHeader) // append questions container header
            questionsContainer.append(librariesQuestionsListContainer)

            var libraryquestionsList = testLibraries[lib]['questionsList']
            for(var ques = 0; ques < libraryquestionsList.length; ques++){

                var quesId = libraryquestionsList[ques]['id']
                var quesContainer = document.createElement('div')
                quesContainer.classList.add('px-3','py-2')
                quesContainer.id = 'question_'+quesId+'_'+testId
                quesContainer.innerText = libraryquestionsList[ques]['question'] + libraryquestionsList[ques]['question'] + libraryquestionsList[ques]['question']

                var questionSeprator = document.createElement('hr');
                questionSeprator.classList.add('hrElement');
                questionSeprator.style.borderColor = '#dbdbe1 !important;';

                librariesQuestionsListContainer.append(quesContainer)
                librariesQuestionsListContainer.append(questionSeprator)

            }

            if (typeof PerfectScrollbar !== 'undefined') {
                new PerfectScrollbar(librariesQuestionsListContainer);
            } else {
                console.warn('Perfect Scrollbar library not found!');
            }
        }
    }

}