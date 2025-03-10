var perviousLibrary
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
var createNewPaper = {}
var tempPaper
var selectedPaper = {}
var JdStatus = ''
var nextStatus
var totalinterviwersLst
// var createTestCard = true


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
                createTest(res.data['workFlowData'],'edit')
                totalinterviwersLst = res.data['selectedJDInterviewers']
                JdStatus = res.data['jdStatus']
                changeStatusInHtml(res.data['jdStatus'])
                // deleteTestValidation(res.data['jdStatus'])

                if (res.data['workFlowData'].length == 0){
                    setUpInstructions()
                }

            }
        }

    })

}


function changeStatusInHtml(changeStatus){
    
    if(changeStatus == 'D'){
        document.getElementById('JdStatusShowElement').innerText = 'Publish'
    }
    
    if(changeStatus == 'A'){
        document.getElementById('JdStatusShowElement').innerText = 'Stop'
    }

    if(changeStatus == 'P'){ // Paused JD
        document.getElementById('JdStatusShowElement').innerText = 'Publish'
    }

}


function openPublishJd(){

    if(totalinterviwersLst != 0){

        var totalTestLst = Object.keys(testsList).length

        if(totalTestLst == 0){
            $('#jdPublishValidators').modal('show')
        }
        else{

            if(JdStatus == 'D'){
                changeStatusInHtml('D')
                nextStatus = 'A'
                document.getElementById('publishConformationCloseBtn').classList.remove('margin-top-adjust_one','margin-top-adjust_two');
                document.getElementById('publishConformationCloseBtn').classList.add('margin-top-adjust_three');
                document.getElementById('conformationPublish').innerHTML = "One's Publish you can not delete any of the tests"
                document.getElementById('publishJdConform').innerText = 'Publish'
                $('#JdPublishConformation').modal('show')
            }
            
            if(JdStatus == 'A'){
                changeStatusInHtml('A')
                nextStatus = 'P'
                document.getElementById('conformationPublish').innerHTML = "Do you want to stop registering candidates to this JD"
                document.getElementById('publishConformationCloseBtn').classList.remove('margin-top-adjust_one','margin-top-adjust_three');
                document.getElementById('publishConformationCloseBtn').classList.add('margin-top-adjust_two');
    
                document.getElementById('publishJdConform').innerText = 'Confirm'
                $('#JdPublishConformation').modal('show')
            }
    
            if(JdStatus == 'P'){ // Paused JD
                changeStatusInHtml('P')
                nextStatus = 'A'
                document.getElementById('conformationPublish').innerHTML = "Do you want to publish this JD again"
                document.getElementById('publishConformationCloseBtn').classList.remove('margin-top-adjust_two','margin-top-adjust_three');
                document.getElementById('publishConformationCloseBtn').classList.add('margin-top-adjust_one');
                document.getElementById('publishJdConform').innerText = 'Publish'
                $('#JdPublishConformation').modal('show')
            }

        }

    }
    else{
        
        $('#InterviewValidationModal').modal('show')
        
    }

}


// this function call when click on client career page integrations script button
function OpenIntegrationModal(){
    
    if(JdStatus == 'A'){
        $('#jd_integration_modal').modal('show')
    }
    else{
        var jdTitle = document.getElementById('JDTitle').innerText
        document.getElementById('carrersPageIntegrationValidation').innerText = jdTitle +' JD is not Published.'
        $('#integrationValidationJd').modal('show')
    }
}


//  create cards by calling this function 
function createTest(data){
    if(data.length > 0){
        for(var test = 0; test < data.length; test++){
            addTestCardToShow(data[test]['papertitle'], data[test]['promot'],data[test]['papertype'],data[test])  
            
            var key_ = data[test]['id']
            testsList[[key_]] =  data[test]
            testsList_.push(key_)
    
        }
        createWorkFlowContainer(data)
    }
    else{
        clickAnyWhereIn()
    }
}


function clickAnyWhereIn(){}


// create a container that holds libraries container and Select paper container
function createWorkFlowContainer(data){
    
    var mainContainer = document.getElementById('librarysMainContainer')

    if(data.length > 0){

        for(var containerCount = 0; containerCount < data.length; containerCount++){

            var workFlowContainer = document.createElement('div')
            workFlowContainer.id = 'workFlowContainer_'+data[containerCount]['id']
            workFlowContainer.style.paddingBottom = '1rem'
            workFlowContainer.hidden = true
            mainContainer.append(workFlowContainer)

            if(containerCount == 0){

                document.getElementById('workFlowContainer_'+data[containerCount]['id']).hidden = false
                if(document.getElementById(data[containerCount]['papertype']+'_'+data[containerCount]['id'])){
                    document.getElementById(data[containerCount]['papertype']+'_'+data[containerCount]['id']).click()
                }
                
            }

        }

    }

}


// This function html for showing libraries list
function AppendSectionsAndQuestions(data, TestCardId) {

    TestWithLibrariesAndQuestions[TestCardId] = data;

    var subLibraryConttainer = document.createElement('div');
    subLibraryConttainer.id = 'library_sub_container_' + TestCardId;
    subLibraryConttainer.classList.add('py-3', 'library_sub_container', 'fade-in', 'pb-0');

    var sideLibraryTitlesContainer = document.createElement('div');
    sideLibraryTitlesContainer.id = 'sectionTitlesContainer';
    sideLibraryTitlesContainer.dataset['TestCardId'] = TestCardId;
    sideLibraryTitlesContainer.classList.add('Librarys_container', 'overflow-hidden', 'ps', 'ps--active-y', 'libraryContainerFnd', 'fade-in');

    var selectedLibraryQuestionsContainer = document.createElement('div');
    selectedLibraryQuestionsContainer.style.width = '100%';

    var titleUseTemplateContainer = document.createElement('div');
    titleUseTemplateContainer.classList.add('selectedLibraryTitltandUserTemplateContainer');

    var selectedLibraryTitle = document.createElement('h4');
    selectedLibraryTitle.classList.add('questions_container_selected_title');
    selectedLibraryTitle.id = 'librarySelectedTestName_' + TestCardId;

    var useTemplateButton = document.createElement('button');
    useTemplateButton.classList.add('btn', 'btn-lg', 'btn-primary', 'use_template_cust_btn');
    useTemplateButton.innerText = 'Use Library';
    useTemplateButton.id = 'selectedLibrary_' + TestCardId;
    useTemplateButton.dataset['libraryid'] = '';
    useTemplateButton.onclick = () => showQuestionConatainer('useTemplate');

    titleUseTemplateContainer.append(selectedLibraryTitle);
    titleUseTemplateContainer.append(useTemplateButton);

    var librariesQuestionsListContainer = document.createElement('div');
    librariesQuestionsListContainer.id = 'question_container_vertical_scroll';
    librariesQuestionsListContainer.dataset['TestCardId'] = TestCardId;
    librariesQuestionsListContainer.classList.add('questions', 'container', 'Librarys_questions_container', 'questionContainerFnd', 'overflow-hidden', 'ps', 'ps--active-y', 'fade-in');
    librariesQuestionsListContainer.style.paddingLeft = '1rem';
    librariesQuestionsListContainer.style.paddingRight = '0rem';

    // Append the containers
    subLibraryConttainer.append(sideLibraryTitlesContainer);
    selectedLibraryQuestionsContainer.append(titleUseTemplateContainer);
    selectedLibraryQuestionsContainer.append(librariesQuestionsListContainer);
    subLibraryConttainer.append(selectedLibraryQuestionsContainer);

    var workFLowContainer = document.getElementById('workFlowContainer_' + TestCardId);
    workFLowContainer.append(subLibraryConttainer);

    var SelectedPaperQuestionsContainer = document.createElement('div');
    SelectedPaperQuestionsContainer.id = 'selectedLibraryQuestionsContainer_' + TestCardId;
    SelectedPaperQuestionsContainer.hidden = true;
    SelectedPaperQuestionsContainer.classList.add('selectedLibrary');
    workFLowContainer.append(SelectedPaperQuestionsContainer);

    var LibraryQuestionsList;
    instialLibrarySelection[TestCardId] = [];

    for (var lib = 0; lib < data.length; lib++) {
        LibraryQuestionsList = data[lib]['questionsList'];

        instialLibrarySelection[TestCardId].push(data[lib]['id']);

        if (LibraryQuestionsList.length > 0) {

            var questionLibraryContainer = document.createElement('div');
            questionLibraryContainer.id = 'Questions_Library_' + data[lib]['id'];
            questionLibraryContainer.style.paddingRight = '1rem';

            for (var ques = 0; ques < LibraryQuestionsList.length; ques++) {
                var questionContainer = document.createElement('div');
                questionContainer.classList.add('each_question_container', 'my-2', 'slide-in');

                var questionText = document.createElement('div');
                var cleanedQuestion = LibraryQuestionsList[ques].question
                    .replace(/\\u[0-9A-Fa-f]{4}/g, '')
                    .replace(/\s+/g, ' ');

                questionText.innerText = (ques + 1) + ' . ' + cleanedQuestion;
                // star showing before selecting library
                var questionStarContainer = document.createElement('div');
                questionStarContainer.innerHTML = ('<i class="far fa-star"></i>')
                if (LibraryQuestionsList[ques].starquestion == 'Y'){
                    questionStarContainer.innerHTML = ('<i class="fas fa-star"></i>')
                }

                questionContainer.append(questionText);

                // interview questions does not have star Question feature 
                if(LibraryQuestionsList[ques].question_type != 'I'){
                    questionContainer.append(questionStarContainer);
                }

                questionLibraryContainer.append(questionContainer);

                var questionSeprator = document.createElement('hr');
                questionSeprator.classList.add('hrElement');
                questionSeprator.style.borderColor = '#dbdbe1 !important;';

                questionLibraryContainer.append(questionSeprator);
            }

            var fndLibraryContainer = document.getElementsByClassName('libraryContainerFnd');

            for (var container_fnd = 0; container_fnd < fndLibraryContainer.length; container_fnd++) {
                var containerWorkFlowID = fndLibraryContainer[container_fnd].dataset.TestCardId;

                if (containerWorkFlowID == TestCardId) {
                    fndLibraryContainer[container_fnd].insertAdjacentHTML('beforeend', '<div class="py-2 px-2 my-2 mx-3 cust_cursor library_seprator custm_margin_to_selected_library" id="library_' + data[lib]['id'] + '_' + TestCardId + '" onclick="selectLibrary(this.id,' + data[lib]['id'] + ',' + TestCardId + ')">' + data[lib]['title'] + '</div>');
                }
            }

            if (lib == 0) {
                document.getElementById('library_' + data[lib]['id'] + '_' + TestCardId).classList.add('active_selected_library');
                perviousLibrary = data[lib]['id'];
                document.getElementById('librarySelectedTestName_' + TestCardId).innerText = data[lib]['title'];
                document.getElementById('selectedLibrary_' + TestCardId).dataset['libraryid'] = data[lib]['id'];

            } else {
                questionLibraryContainer.hidden = true;
            }

            var fndQuestionsContainer = document.getElementsByClassName('questionContainerFnd');

            for (var container_fnd = 0; container_fnd < fndQuestionsContainer.length; container_fnd++) {
                var containerWorkFlowID = fndQuestionsContainer[container_fnd].dataset.TestCardId;

                if (containerWorkFlowID == TestCardId) {
                    fndQuestionsContainer[container_fnd].append(questionLibraryContainer);
                }
            }

            if (typeof PerfectScrollbar !== 'undefined') {
                new PerfectScrollbar(librariesQuestionsListContainer);
                new PerfectScrollbar(sideLibraryTitlesContainer);
            } else {
                console.warn('Perfect Scrollbar library not found!');
            }
        }
    }

    // Add animation classes after appending
    setTimeout(() => {
        subLibraryConttainer.classList.add('fade-in-active');
        sideLibraryTitlesContainer.classList.add('fade-in-active');
        librariesQuestionsListContainer.classList.add('fade-in-active');

        // Add slide-in effect to question containers
        if(questionLibraryContainer){
            var questionContainers = questionLibraryContainer.querySelectorAll('.each_question_container');
            questionContainers.forEach((container, index) => {
                setTimeout(() => {
                    container.classList.add('slide-in-active');
                }, index * 100); // Stagger animations
            });
        }
    }, 50); // Small delay to ensure elements are in the DOM before animating

}


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
    document.getElementById('holdInputContainer').style.display = 'none'
    document.getElementById('testHold').checked = false;

    var testName
    if (testType == 'screening'){
        testName = 'Screening'
        document.getElementById('promotLevelContainer').hidden = false;
        document.getElementById('holdContainer').hidden = false;
    }
    else if(testType == 'coding'){
        testName = 'Coding'
        document.getElementById('promotLevelContainer').hidden = false;
        document.getElementById('holdContainer').hidden = false;
    }
    else if(testType == 'interview'){
        testName = 'Interview'
        document.getElementById('promotLevelContainer').hidden = true;
        document.getElementById('holdContainer').hidden = true;
    }

    if(testName){
        document.getElementById('modalCenterTitle').innerText = testName
        document.getElementById('testType').value = testName
        document.getElementById('promot_level').value = 80
        document.getElementById('holdPercentage').value = 60
        document.getElementById('testType').dataset['test_type'] = testName
    }

    document.getElementById('holdInfo').innerText = 'Below the Promote percentage candidate will be rejected'

}


// function donotAllowInterviewFirst(testType){
    
//     var lstOfTest = Object.keys(testsList).length

//     if (testType == 'Screening' || testType == 'Coding' || testType == 'S' || testType == 'E'){
//         createTestCard = true
//     }
//     else if(testType == 'Interview' || testType == 'I'){
//         if (lstOfTest > 0){
//             createTestCard = true
//         }
//         else{
//             $('#modalCenter').modal('hide') 
//             $('#InterviewValidationModal').modal('show')
//         }

//     }

// }


// this function send hr selected test to backend
function saveOrUpdateTest(){
    
    var testName = document.getElementById('testType').value;
    var promotValue = document.getElementById('promot_level').value;
    var holdCheck = document.getElementById('testHold');
    var testNameValidator = document.getElementById('test_name_validator');
    var promotValidator = document.getElementById('promot_validator');
    var testType = document.getElementById('testType').dataset.test_type
    var saveTest = true;
    var testHoldYesOrNo = 'N'
    var holdPercenTageVal 

    if(holdCheck.checked){
        testHoldYesOrNo = 'Y'
        var holdPercentageValue = document.getElementById('holdPercentage')

        if (!holdPercentageValue.value){ // input is empty this will call
            saveTest = false
            hold_validator.hidden = false
        }
        else{ // input has value
            holdPercenTageVal = parseInt(holdPercentageValue.value)
            hold_validator.hidden = true
        }

    }

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

    var questionTitle = document.getElementById('questionPaperTitle_'+cureentTestId)
    if(questionTitle){
        questionTitle.innerText = testName
    }
    
    // donotAllowInterviewFirst(testType)
    
    // if(createTestCard){

        if(saveTest){
            
            $('#modalCenter').modal('hide')
    
            if (testCreateOrUpdate == 'create'){
    
                dataObj = {
                    'createOrUpdate'  : testCreateOrUpdate,
                    'testName'        : testName,
                    'promotPercentage': promotValue,
                    'testType'        : testType,
                    'holdYesOrNo'     : testHoldYesOrNo,
                    'holdvalue'       : holdPercenTageVal,
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
                    'holdYesOrNo'     : testHoldYesOrNo,
                    'holdvalue'       : holdPercenTageVal,
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

                            if(data['paperid']){

                                dataObj = {
                                    'event':'update',
                                    'paperId': data['paperid'],
                                    'paperTitle': data['papertitle'],
                                    'promotPercentage':data['promot'],
                                    'holdYesOrNo'     : testHoldYesOrNo,
                                    'holdvalue'       : holdPercenTageVal,
                                }
                                
                                var final_data = {
                                    'data': JSON.stringify(dataObj),
                                    csrfmiddlewaretoken: CSRF_TOKEN,
                                }
                                
                                $.post(CONFIG['acert'] + "/api/update-paperdetails", final_data, function (res) {
    
                                })
                            }

                        }
                        else{
                            // test is add and create card
                            
                            var key_ = data[0]['id'] // test card id
                            testsList[[key_]] =  data[0]
                            testsList_.push(key_)
                            
                            var mainContainer = document.getElementById('librarysMainContainer')
    
                            if(data.length > 0){
    
                                var workFlowContainer = document.createElement('div')
                                workFlowContainer.id = 'workFlowContainer_'+key_
                                workFlowContainer.style.paddingBottom = '1rem'
                                workFlowContainer.hidden = false
                                mainContainer.append(workFlowContainer)
    
                            }
    
                            testType = testType
                            addTestCardToShow(testName,promotValue,testType,data[0])
    
                            document.getElementById(data[0]['papertype']+'_'+data[0]['id']).click();
    
                        }
    
                    }
                }
    
            })
    
        }
    // }
}


function updateCardAfterSaveData(allTestsList,testId){
    console.log('allTestsList :: ',allTestsList);
    var testType = allTestsList[testId]['papertype']
    var testName
    if (testType == 'S'){
        testName = 'Screening'
        document.getElementById('testTitle_'+testId).innerText = allTestsList[testId]['papertitle']
        document.getElementById('testCardTestType_'+testId).innerText = ""+testName+"( Promote % "+allTestsList[testId]['promot']+" )"
    }
    else if(testType == 'E'){
        testName = 'Coding'
        document.getElementById('testTitle_'+testId).innerText = allTestsList[testId]['papertitle']
        document.getElementById('testCardTestType_'+testId).innerText = ""+testName+"( Promote % "+allTestsList[testId]['promot']+" )"
    }
    else if(testType == 'I'){
        testName = 'Interview'
        document.getElementById('testTitle_'+testId).innerText = allTestsList[testId]['papertitle']
        document.getElementById('testCardTestType_'+testId).innerText = ""+testName
    }

}


function addTestCardToShow(testName, promotValue, testType, data) {
    var testCardsContainer = document.getElementById('testCards');
    var testTypeColor;
    var testTitle;
    var testIcon;
    var testDesc;
    var testLabel;

    if (testType == 'S' || testType == 'Screening') {
        testTypeColor = screeningBackgroundColor;
        testTitle = 'S';
        testDesc = 'Screening';
        testIcon = '<i class="fas fa-clipboard-check" style="margin-right:12px;color:' + screenMainColor + ';font-size:2rem;"></i>';
        testLabel = `<p class="text-muted small mb-0" id="testCardTestType_${data['id']}">${testDesc} (Promote % ${promotValue})</p>`

    } else if (testType == 'E' || testType == 'Coding') {
        testTypeColor = codingBackgroundColor;
        testTitle = 'E';
        testDesc = 'Coding';
        testIcon = '<i class="fas fa-code" style="margin-right:12px;color:' + codingMainColor + ';font-size:2rem;"></i>';
        testLabel = `<p class="text-muted small mb-0" id="testCardTestType_${data['id']}">${testDesc} (Promote % ${promotValue})</p>`

    } else if (testType == 'I' || testType == 'Interview') {
        testTypeColor = interviewBackgroundColor;
        testTitle = 'I';
        testDesc = 'Interview';
        testIcon = '<i class="fas fa-chalkboard-teacher" style="margin-right:12px;color:' + interviewMainColor + ';font-size:2rem;"></i>';
        testLabel = `<p class="text-muted small mb-0" id="testCardTestType_${data['id']}">${testDesc}</p>`

    }

    // Create a new div for the card
    var cardHTML = `
        <div class="col-sm-6 col-lg-4 mb-4" id="testCardSubContainer_${data['id']}" style="padding-left:0px !important; padding-right: calc(var(--bs-gutter-x)* 0.9);">
            <div class="card p-3 cust_cursor shadow-sm fade-in workFlowTestCards" style="background-color: ${testTypeColor}; border-radius: 8px;" onclick="selectTest(this.id)" id="${testTitle}_${data['id']}">
                <figure class="m-0">
                    <blockquote class="blockquote m-0">
                        <div class="d-flex align-items-center mb-3">
                            <div class="me-2">
                                ${testIcon}
                            </div>
                            <div>
                                <span id="testTitle_${data['id']}" class="fw-bold text-dark">${testName}</span>
                                ${testLabel}
                            </div>
                        </div>
                    </blockquote>
                </figure>
                <div class="d-flex justify-content-between mt-0 pt-0"> 
                    <i class="bx bx-edit custm-edit-icon" id="editTestCard_${data['id']}" onclick="updateTest(event, ${data['id']})" style="cursor: pointer;"></i>
                    <button class="deleteFontIcon perventDeleteBtn" data-bs-toggle="modal" onclick="deleteTestModalOpen(${data['id']})"  style="cursor: pointer; display: flex; align-items: center; justify-content: center; background-color: transparent;">
                        <i class='bx bx-trash' ></i>
                    </button>
                </div>
            </div>
        </div>`;

    // Insert the card HTML into the container
    testCardsContainer.insertAdjacentHTML('beforeend', cardHTML);

    // Trigger the fade-in animation
    var newCard = document.getElementById(testTitle + '_' + data['id']);
    requestAnimationFrame(() => {
        newCard.classList.add('visible'); // This will trigger the CSS animation
    });
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
        
        var custumStyles
        
        if(test_type == 'S'){
            custumStyles = 'activeTestCars-screen-test'
        }
        if(test_type == 'E'){
            custumStyles = 'activeTestCars-coding-test'
        }
        if(test_type == 'I'){
            custumStyles = 'activeTestCars-interview-test'
        }

        var testBox = document.getElementById(element_id)
        // testBox.style.border = '1px solid ' + custumStyles
        // testBox.style.boxShadow = '0 2px 6px 0 rgba(79, 80, 82, 0.56)';
        testBox.classList.remove('unActiveTestCard')
        testBox.classList.add(custumStyles)


        if (perviousSelectedTest){
            var testBox = document.getElementById(perviousSelectedTest)
            if(testBox){
                testBox.classList.remove('activeTestCars-screen-test', 'activeTestCars-coding-test', 'activeTestCars-interview-test')
                testBox.classList.add('unActiveTestCard')
            }
            // testBox.style.border = ''
            // testBox.style.boxShadow = '0 2px 6px 0 rgba(67, 89, 113, 0.12)';
        }
        
    }
    
    perviousSelectedTest = element_id
    document.getElementById('librarysMainContainer').hidden = false

}


function updateTest(event, currentSelectedtestId) {
    testCreateOrUpdate = 'update';
    cureentTestId = currentSelectedtestId;
    event.stopPropagation();
    openUpdateTestModel(currentSelectedtestId);
}


function openUpdateTestModel(currentSelectedtestId) {
    if (currentSelectedtestId) {
        
        var testType = testsList[currentSelectedtestId]['papertype'];
        var holdStatus = testsList[currentSelectedtestId]['hold']
        var holdPercentageValue = testsList[currentSelectedtestId]['holdpercentage']

        var holdMainContainer = document.getElementById('holdContainer')
        var holdElement = document.getElementById('testHold')
        var holdInputContai = document.getElementById('holdInputContainer') 
        var holdInfo = document.getElementById('holdInfo') 

        if(holdStatus == 'Y'){
            holdElement.checked = true
            document.getElementById('holdPercentage').value = holdPercentageValue
            holdInputContai.style.display = 'block'
            holdInfo.innerText = 'Below the Hold percentage candidate will be rejected'
        }
        else{
            holdElement.checked = false
            holdInputContai.style.display = 'none'
            holdInfo.innerText = 'Below the Promote percentage candidate will be rejected'
        }

        var testName;

        if (testType == 'screening' || testType == 'S') {
            testName = 'Screening';
            document.getElementById('promotLevelContainer').hidden = false;
            holdMainContainer.hidden = false
        } 
        else if (testType == 'coding' || testType == 'E') {
                testName = 'Coding';
                document.getElementById('promotLevelContainer').hidden = false;
                holdMainContainer.hidden = false
        }
        else if (testType == 'interview' || testType == 'I') {
                testName = 'Interview';
                document.getElementById('promotLevelContainer').hidden = true;
                holdMainContainer.hidden = true
        }

        var modalTitle = document.getElementById('modalCenterTitle');
        var testTypeInput = document.getElementById('testType');
        var promotLevelInput = document.getElementById('promot_level');

        modalTitle.innerText = testName;
        testTypeInput.value = testsList[currentSelectedtestId]['papertitle'];
        promotLevelInput.value = testsList[currentSelectedtestId]['promot'];
        testTypeInput.dataset['test_type'] = testsList[currentSelectedtestId]['papertype'];

        // Add fade-in animation
        $('#modalCenter').modal('show').addClass('fade-in');
    }
}


document.getElementById('script_copy_btn').addEventListener('click', function () {
    var scriptValue = document.getElementById('scriptTextarea').value;
    var functionValue = document.getElementById('functionTextarea').value;
    var combinedText = `${scriptValue}\n${functionValue}`;

    navigator.clipboard.writeText(combinedText).then(() => {
        var scriptTextarea = document.getElementById('scriptTextarea');
        var functionTextarea = document.getElementById('functionTextarea');

        // Add flash-border animation
        scriptTextarea.classList.add('flash-border');
        functionTextarea.classList.add('flash-border');

        setTimeout(() => {
            scriptTextarea.classList.remove('flash-border');
            functionTextarea.classList.remove('flash-border');
        }, 500);

    }).catch(err => {
        console.error('Error copying text: ', err);
    });
});


function getPapersLibraries(test_type, workFlowId) {

    checkTestHasPaper(workFlowId).then(testPaperData => {
        var workflowContainer = document.getElementById(`workFlowContainer_${workFlowId}`);
        var questionsContainer = document.getElementById(`selectedLibraryQuestionsContainer_${workFlowId}`);
        var libraryContainer = document.getElementById(`library_sub_container_${workFlowId}`);

        if (testPaperData['paperId'] == 'N') { // Show libraries if no paper ID
             
            var dataObj = {
                'jdLibId': parseInt(jdlibraryid),
                'LibType': test_type // Paper Type
            };

            var final_data = {
                'data': JSON.stringify(dataObj),
                csrfmiddlewaretoken: CSRF_TOKEN,
            };

            $.post(CONFIG['acert'] + "/api/libraries", final_data, function (res) {
                if (res.statusCode == 0 && res.data) {
                    AppendSectionsAndQuestions(res.data['librariesList'], workFlowId);
                }
            }).fail(function (error) {
                console.error("API request failed:", error);
            });

        } else {
            // this code excuites after paper created
            // console.log('testPaperData :: ',testPaperData);
            var dataObj = {
                'jdLibId': parseInt(jdlibraryid),
                'LibType': testPaperData['paperType'],
                'paperId': testPaperData['paperId'],
                'paperLibraryId':testPaperData['libraryId']
            };

            var final_data = {
                'data': JSON.stringify(dataObj),
                csrfmiddlewaretoken: CSRF_TOKEN,
            };

            $.post(CONFIG['acert'] + "/api/libraries", final_data, function (res) {
                
                if (res.statusCode == 0 && res.data) {
                    
                    // if library paper was set to not a library paper questions was not appear on the screen
                    // it will excuite after paper create.
                    tempPaper = res.data['paper']
                    TestWithLibrariesAndQuestions[workFlowId] = res.data['librariesList'];
                    createQuestionsContainer(workFlowId, testPaperData['libraryId'], tempPaper, res['data']['starQuestionsLst']);

                }
            }).fail(function (error) {
                console.error("API request failed:", error);
            });
        }
    }).catch(error => {
        console.error("Error checking test has paper:", error);
    });
}


function checkTestHasPaper(workFlowId) {
    var dataObj = {
        'workFlowId': parseInt(workFlowId),
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


function showQuestionConatainer(event) { // Where ever we click on the use Template button this function will call
    
    if (event == 'useTemplate') {
        
        for (let testCount = 0; testCount < testsList_.length; testCount++) {
            var testId = testsList_[testCount];
            var testElementId = `workFlowContainer_${testId}`;
            var workFLowContainer = document.getElementById(testElementId);

            if (workFLowContainer.hidden == false) {

                var testIdStoreContainer = testId

                var selectedLibraryQuestionsContainer = document.getElementById(`selectedLibraryQuestionsContainer_${testId}`);
                selectedLibraryQuestionsContainer.classList.add('slide-down');
                selectedLibraryQuestionsContainer.hidden = false; // un hidding

                document.getElementById(`library_sub_container_${testId}`).hidden = true;
                
                var selectedLibrary__ = document.getElementById(`selectedLibrary_${testId}`).dataset['libraryid'];

                // this function create a paper save Paper in acert
                var paperCreatedData = createPaper(selectedLibrary__, testId, 'useTemplate');
                paperCreatedData.then(
                    (responseData) => {
                        // this will excuite when use click on uselibrary button 
                        // it will create HTML and show on static and Dynamic Questions on webapge
                        // console.log('responseData :: ',responseData['starQuestionsLst']);
                        createQuestionsContainer(testIdStoreContainer, selectedLibrary__, responseData, responseData['starQuestionsLst']);
                    }
                ).catch(
                    (error) => {
                        console.error('Error:', error);
                    }
                );

            }
        }
    }
}


// it will create HTML and show on static and Dynamic Questions on webapge
function createQuestionsContainer(testId, librarieId, selectedPaper, starQuestionList) { 

    testsList[testId]['paperlibraryid'] = librarieId
    
    var selectedLibraryId;
    var buttonData = document.getElementById('selectedLibrary_' + testId);

    if (buttonData) { // when use template button  click 
        selectedLibraryId = buttonData.dataset['libraryid'];
    } else { // this code will excuite after paper create
        selectedLibraryId = librarieId;
    }
    
    var testLibraries = TestWithLibrariesAndQuestions[testId];

    for (var lib = 0; lib < testLibraries.length; lib++) {

        var librariesQuestionsListContainer = document.createElement('div');
        librariesQuestionsListContainer.id = 'question_container_vertical_scroll';
        librariesQuestionsListContainer.dataset['TestCardId'] = testId;
        librariesQuestionsListContainer.classList.add('questions', 'Librarys_questions_container', 'questionContainerFnd', 'overflow-hidden', 'ps', 'ps--active-y', 'm-0', 'w-100', 'fade-in'); // Added fade-in class
        librariesQuestionsListContainer.style.paddingLeft = '1rem';
        librariesQuestionsListContainer.style.paddingRight = '0rem';
        librariesQuestionsListContainer.style.width = '100%';
        
        if (testLibraries[lib]['id'] == selectedLibraryId) { // libraries loop
            
            var paperTitle_
            var staticQuestionCountNum
            var dynamicQuestionCountNum
            
            if(selectedPaper){
                
                paperTitle_ = selectedPaper['papertitle']
                staticQuestionCountNum = selectedPaper['staticQuestionsCount']
                dynamicQuestionCountNum = selectedPaper['dynamicQuestionsCount']

                var testTitle = document.getElementById('testTitle_'+testId)
                if(testTitle){
                    paperTitle_ = testTitle.innerText
                }

            }
            else{
                var testTitleInnerText = document.getElementById('testTitle_'+testId).innerText
                paperTitle_ = testTitleInnerText
                staticQuestionCountNum = testLibraries[lib]['questionsList'].length
                dynamicQuestionCountNum = 0
            }

            var staticQuestionsContainer = document.createElement('div');
            staticQuestionsContainer.classList.add('staticQuestionsContainer', 'fade-in'); // Added fade-in class

            var staticContainerHeading = document.createElement('h5');
            staticContainerHeading.innerText = 'Static';
            staticContainerHeading.classList.add('static_or_dynamic_text_container_headings');

            if(testLibraries[lib]['papertype'] == "I"){
                
            }
            else{
                staticQuestionsContainer.append(staticContainerHeading);
            }

            var dynamicQuestionsContainer = document.createElement('div');
            dynamicQuestionsContainer.classList.add('dynamicQuestionsContainer', 'fade-in'); // Added fade-in class

            var titleAndInputContainer = document.createElement('div');
            titleAndInputContainer.classList.add('titleAndContainerDynamic');

            var labelInputContainer = document.createElement('div');
            labelInputContainer.classList.add('titleInputContainer');

            var labelForDynamicInputField = document.createElement('div');
            labelForDynamicInputField.innerText = 'Dynamic Questions Count';
            labelForDynamicInputField.classList.add('mx-4');

            var dynamicQuestionCountInpt = document.createElement('input');
            dynamicQuestionCountInpt.style.borderWidth = '0.1px'
            dynamicQuestionCountInpt.style.borderColor = 'var(--primary-color)'
            dynamicQuestionCountInpt.type = 'number';
            dynamicQuestionCountInpt.classList.add('form-control', 'inputCustWidth');
            dynamicQuestionCountInpt.id = 'dynamicQuestionsCount_' + testId;

            labelInputContainer.append(labelForDynamicInputField);
            labelInputContainer.append(dynamicQuestionCountInpt);

            var dynamicContainerHeading = document.createElement('h5');
            dynamicContainerHeading.innerText = 'Dynamic';
            dynamicContainerHeading.classList.add('static_or_dynamic_text_container_headings');
            titleAndInputContainer.append(dynamicContainerHeading);
            titleAndInputContainer.append(labelInputContainer);
            dynamicQuestionsContainer.append(titleAndInputContainer);

            var questionContainerHeader = document.createElement('div');
            questionContainerHeader.classList.add('question_container_header');

            if (testLibraries[lib]['papertype'] == 'S' || testLibraries[lib]['papertype'] == "E" || testLibraries[lib]['papertype'] == "I") {

                var selectedLibraryTitle = document.createElement('h4');
                selectedLibraryTitle.id = 'questionPaperTitle_'+testId
                selectedLibraryTitle.classList.add('py-2', 'm-0', 'p-clr');
                selectedLibraryTitle.innerText = paperTitle_;
                selectedLibraryTitle.style.width = 'max-content';

                var questionsCountContainer = document.createElement('div'); // Static & Dynamic Questions count container
                questionsCountContainer.style.display = 'flex';
                questionsCountContainer.style.alignItems = 'center'; 
                questionsCountContainer.id = 'questionsCountContainer';

                var staticQuestionContainer = document.createElement('div');
                staticQuestionContainer.style.display = 'flex';

                if(testLibraries[lib]['papertype'] == "I"){
                    staticQuestionContainer.style.marginRight = '10px'
                }

                var staticQuestionlabel = document.createElement('div');
                staticQuestionlabel.innerText = 'Static Questions';
                
                var staticQuestionCounBox = document.createElement('div');
                staticQuestionCounBox.id = 'static_questions_count_'+testId;
                staticQuestionCounBox.classList.add('mx-1')
                staticQuestionCounBox.innerText = staticQuestionCountNum;

                var dynQuestionContainer = document.createElement('div');
                dynQuestionContainer.style.display = 'flex';
                dynQuestionContainer.classList.add('mx-3');

                var dynQuestionlabel = document.createElement('div');
                dynQuestionlabel.innerText = 'Dynamic Questions';
                
                var dynQuestionCounBox = document.createElement('div');
                dynQuestionCounBox.classList.add('mx-1')
                dynQuestionCounBox.id = 'dynamic_questions_count_'+testId;
                dynQuestionCounBox.innerText = dynamicQuestionCountNum;

                var saveButtonToContainer = document.createElement('button')
                saveButtonToContainer.id = 'saveQuestions_'+testId;
                saveButtonToContainer.innerText = 'Save';
                saveButtonToContainer.classList.add('btn', 'btn-primary')
                saveButtonToContainer.dataset.testid = testId
                saveButtonToContainer.onclick = function() {
                    return savePaper(this, this.id, testId, selectedPaper);
                };

                staticQuestionContainer.append(staticQuestionlabel, staticQuestionCounBox);
                dynQuestionContainer.append(dynQuestionlabel, dynQuestionCounBox);
                
                if(testLibraries[lib]['papertype'] == "I"){
                    questionsCountContainer.append(staticQuestionContainer, saveButtonToContainer);    
                }
                else{
                    questionsCountContainer.append(staticQuestionContainer, dynQuestionContainer, saveButtonToContainer);
                }
                
                questionContainerHeader.append(selectedLibraryTitle, questionsCountContainer);

                var questionsContainer = document.getElementById('selectedLibraryQuestionsContainer_' + testId);
                if (questionsContainer) {
                    questionsContainer.append(questionContainerHeader, librariesQuestionsListContainer);
                } else {
                    var questionsContainer = document.createElement('div');
                    questionsContainer.id = 'selectedLibraryQuestionsContainer_' + testId;
                    document.getElementById('workFlowContainer_' + testId).append(questionsContainer);
                    questionsContainer.append(questionContainerHeader, librariesQuestionsListContainer);
                }

                var libraryquestionsList = testLibraries[lib]['questionsList'];

                for (var ques = 0; ques < libraryquestionsList.length; ques++) { // Questions List 

                    // console.log('selec Paper id ::--',selectedPaper['paperQuestionslst'][ques]['id'], 'Lib ::--',libraryquestionsList[ques]['question_id']);

                    // var libraryQuesId = libraryquestionsList[ques]['question_id']
                    // var selectedPaperQuesId
                    var staticCheckbox__ = true
                    var dynamicCheckbox__ = false

                    // if(selectedPaper['paperQuestionslst'][ques]){
                    //     console.log('++',selectedPaper['paperQuestionslst'][ques]);
                    //     selectedPaperQuesId = selectedPaper['paperQuestionslst'][ques]['id']
                    // }

                    if(selectedPaper){

                        staticCheckbox__ = false
                        dynamicCheckbox__ = false

                    }
                    // else{

                    //     var staticCheckbox__ = true
                    //     var dynamicCheckbox__ = false

                    // }

                    var questionContainer = document.createElement('div');
                    questionContainer.classList.add('each_question_container', 'my-2', 'slide-in'); // Added slide-in class

                    var quesId = libraryquestionsList[ques]['question_id'];
                    var questionText = document.createElement('div');
                    questionText.classList.add('px-3', 'py-2');
                    questionText.style.width = '90%'
                    questionText.id = 'question_' + quesId + '_' + testId;
                    var cleanedQuestion = libraryquestionsList[ques]['question'].replace(/\\u[0-9A-Fa-f]{4}/g, '').replace(/\s+/g, ' ');
                    questionText.innerText = (ques + 1) + ' . ' + cleanedQuestion;

                    var questionCheckBoxContainer = document.createElement('div');
                    questionCheckBoxContainer.style.position = 'relative';
                    
                    var Star
                    if(testLibraries[lib]['papertype'] == "I"){
                        Star = ''
                    }
                    else{
                        questionCheckBoxContainer.style.width = '65px'
                        questionCheckBoxContainer.classList.add('checkboxcontainer')
                        var starId = `id="staticstarQuestion_${quesId}_${testId}"`
                        // Star = `<i ${starId} class="far fa-star p-clr star_question_" style="font-size:20px; margin-right: 15px; cursor: pointer;" onclick="makeAsStarQuestion(${quesId},${testId})" data-star="" data-bs-toggle="tooltip" data-bs-offset="0,4" data-bs-placement="top" data-bs-html="true" title=""> </i> <img class="blastGif" src="/static/img/illustrations/congratulations-7600-ezgif.com-gif-maker.gif" alt="">`;
                        Star = `<i ${starId} class="far fa-star p-clr star_question_" style="font-size:20px; margin-right: 15px; cursor: pointer;" onclick="makeAsStarQuestion(${quesId},${testId})" data-star="" data-bs-toggle="tooltip" data-bs-offset="0,4" data-bs-placement="top" data-bs-html="true" title=""> </i>`;
                    }

                    // function parameter first parameter is questionId and second Parameter Testid 
                    questionCheckBoxContainer.innerHTML = `${Star}<input type="checkbox" name="" id="questionCheckBox_${quesId}_${testId}" class="form-check-input questionSelect_${testId}" onclick="SelectQuestionOrUnSelectQuestion(this.id,${quesId},${testId})" style="border-color:var(--primary-color);">`;

                    questionContainer.append(questionText, questionCheckBoxContainer);

                    var questionSeprator = document.createElement('hr');
                    questionSeprator.classList.add('hrElement');
                    questionSeprator.style.borderColor = '#dbdbe1';

                    // Cloning for static and dynamic containers
                    var staticClone = questionContainer.cloneNode(true);
                    var dynamicClone = questionContainer.cloneNode(true);
                    
                    var staticCheckbox = staticClone.querySelector('input[type="checkbox"]');

                    if (staticCheckbox) {
                        staticCheckbox.checked = staticCheckbox__;
                        staticCheckbox.dataset['question_type'] = 'S'; // "S" Static type question
                        staticCheckbox.id = `staticQuestionCheckBox_${quesId}_${testId}`;
                    }

                    // Removing Star From Dynamic Questions
                    var dynamicCheckbox = dynamicClone.querySelector('input[type="checkbox"]');
                    var dynamicCheckBoxContainer = dynamicClone.querySelector('.checkboxcontainer');
                    var dynamicStarquestion = dynamicClone.querySelector('.star_question_');
                    if(dynamicStarquestion){
                        dynamicCheckBoxContainer.style.width = 'max-content'
                        dynamicStarquestion.remove()
                    } 

                    if (dynamicCheckbox) {
                        dynamicCheckbox.checked = dynamicCheckbox__;
                        dynamicCheckbox.dataset['question_type'] = 'D'; // "D" Dynamic Type Question
                        dynamicCheckbox.id = `dynamicQuestionCheckBox_${quesId}_${testId}`;
                    }

                    staticQuestionsContainer.append(staticClone, questionSeprator.cloneNode(true));
                    dynamicQuestionsContainer.append(dynamicClone, questionSeprator.cloneNode(true));
                }

                // Interview has only Static questions
                if(testLibraries[lib]['papertype'] == "I"){
                    librariesQuestionsListContainer.append(staticQuestionsContainer);
                }
                else{
                    librariesQuestionsListContainer.append(staticQuestionsContainer, dynamicQuestionsContainer);
                }

                if (typeof PerfectScrollbar !== 'undefined') {
                    new PerfectScrollbar(librariesQuestionsListContainer);
                } else {
                    console.warn('Perfect Scrollbar library not found!');
                }
            }
        }
    }
    if(selectedPaper){
        selectedPaperQuestionsCheck(selectedPaper,testId, starQuestionList)
    }
}

function savePaper(element, element_id, testid_, selectedPaper) {

    if(JdStatus == "D"){
        if (testid_) {

            var testid = Number(testid_);
            var questionsLst = document.getElementsByClassName('questionSelect_' + testid);

            var staticQuesLst = [];
            var dynamicQuesLst = [];

            for (var ques = 0; ques < questionsLst.length; ques++) {
                var questionElement = questionsLst[ques];
                var quesType = questionElement.dataset['question_type'];
                
                if (questionElement.checked) {
                    var quesid = questionElement.id.split('_')[1];

                    if (quesType === 'S') {
                        staticQuesLst.push(quesid);
                    } 
                    else if (quesType === 'D') {
                        dynamicQuesLst.push(parseInt(quesid));
                    }
                }
            }

            var dynamicQuestionValidation = true
            if(dynamicQuesLst.length == 1) {
                dynamicQuestionValidation =  false
                $('#dynamicQuestionsValidators').modal('show')
                document.getElementById('dynamicQuestionsValidator').innerText = "Dynamic Questions Can't be Single Question"
            }

            var dynCount = 0
            var reqDynaminQuestionsCount = document.getElementById('dynamicQuestionsCount_'+testid)
            if(reqDynaminQuestionsCount){
                dynCount = reqDynaminQuestionsCount.value
            }

            // if(dynamicQuesLst.length > 0){
            //     if (dynCount == 0){
            //         dynamicQuestionValidation =  false
            //         $('#dynamicQuestionsValidators').modal('show')
            //         document.getElementById('DynquestionsCount').hidden = false
            //         document.getElementById('dynamicQuestionsValidator').innerText = "Dynamic Questions Count have to Less than total dynamic questions"
            //     }
            // }

            var paper_Title
            var paperTitle__ = document.getElementById('questionPaperTitle_'+testid)
            if(paperTitle__){
                paper_Title = paperTitle__.innerText
            }

            if(dynamicQuestionValidation){

                dataObj = {
                    'event'                : 'updatePaper',
                    'paperid'              : selectedPaper['paperid'],
                    'paperLibraryId'       : testsList[testid_]['paperlibraryid'],
                    'paperTitle'           : paper_Title,
                    'staticQuestionsList'  : staticQuesLst,
                    'dynamicQuestionsList' : dynamicQuesLst,
                    'dynamicQuestionsCount': dynCount
                };
        
                var final_data = {
                    "data":JSON.stringify(dataObj),
                    csrfmiddlewaretoken: CSRF_TOKEN,
                };
        
                $.post(CONFIG['acert'] + "/api/save-paper", final_data, function (res) {
        
                    if(res.statusCode == 0){
                        showSuccessMessage('Test paper created');
                    }
        
                });

            }

        }
    }
    else{
        $('#createPaperStatusValidation').modal('show')
    }
    
}


// it checks hr selected static and dynamic question 
function selectedPaperQuestionsCheck(selectedPaper, testId, starQuestionList){

    var staticQuestionsLst = selectedPaper['paperQuestionslst']
    var dynaminQuestionsLst = selectedPaper['dynamicQuestionIds']

    if(staticQuestionsLst){
        if(staticQuestionsLst.length > 0){
            for( var statQues = 0; statQues < staticQuestionsLst.length; statQues++){
                var questionCheckInpt = document.getElementById('staticQuestionCheckBox_'+staticQuestionsLst[statQues]['id']+'_'+testId)
                if(questionCheckInpt){
                    questionCheckInpt.checked = true
                }
            }
        }
    }
    
    // selecting the questions checkbox
    if(dynaminQuestionsLst){
        if(dynaminQuestionsLst.length > 0){
            for( var dynQues = 0; dynQues < dynaminQuestionsLst.length; dynQues++){
                var questionCheckInpt = document.getElementById('dynamicQuestionCheckBox_'+dynaminQuestionsLst[dynQues]+'_'+testId)
                if(questionCheckInpt){
                    questionCheckInpt.checked = true
                }   
            }
        }
    }

    var dynamicCountElem = document.getElementById('dynamicQuestionsCount_'+testId)
    if(dynamicCountElem){
        dynamicCountElem.value = selectedPaper['dynamicQuestionsInpt']
    }

    if(starQuestionList){

        for (var starQuestion  = 0; starQuestion < starQuestionList.length; starQuestion++ ){
            var staticstarQuestionActiveOrInactive = document.getElementById('staticstarQuestion_'+starQuestionList[starQuestion]['questionId']+'_'+testId)
            
            if (staticstarQuestionActiveOrInactive){
    
                if(starQuestionList[starQuestion]['star'] == 'Y'){
                    staticstarQuestionActiveOrInactive.classList.remove('far'); 
                    staticstarQuestionActiveOrInactive.classList.add('fas');
                    staticstarQuestionActiveOrInactive.dataset['star'] = 'Y'
                }
                else{
                    staticstarQuestionActiveOrInactive.classList.remove('fas');
                    staticstarQuestionActiveOrInactive.classList.add('far');
                    staticstarQuestionActiveOrInactive.dataset['star'] = 'N'
                }
    
                // this star question was not in paper , this is library question so we can't make any change to this question 
                if(starQuestionList[starQuestion]['starDisable'] == 'Y'){
                    staticstarQuestionActiveOrInactive.dataset['disable'] = 'Y'
                    staticstarQuestionActiveOrInactive.style.color = 'gray'
                    staticstarQuestionActiveOrInactive.style.cursor = 'not-allowed';
    
                }
                // this is a star question from Paper
                else{
                    staticstarQuestionActiveOrInactive.dataset['disable'] = 'N'
                }
    
            }
    
        }

    }

}

// add questions and removing questions from the paper by click on the checkbox
function SelectQuestionOrUnSelectQuestion(elementId, questionId, TestId){
    
    var question = document.getElementById(elementId)
    var questionid = elementId.split('_')[1]
    var testid = elementId.split('_')[2]
    var questionTypeDynamicOrStatic = question.dataset['question_type']
    
        if(questionTypeDynamicOrStatic == "D"){

            var staticQuestion = document.getElementById(`staticQuestionCheckBox_${questionid}_${testid}`)
            if(staticQuestion){
                if(staticQuestion.checked){
                    staticQuestion.checked = false
                }
            }

        }

    if(questionTypeDynamicOrStatic == "S"){
        var staticQuestion_ = document.getElementById(`staticQuestionCheckBox_${questionid}_${testid}`)
        var statstarQuestion = document.getElementById(`staticstarQuestion_${questionid}_${testid}`)

        if(staticQuestion_.checked){

            statstarQuestion.dataset['disable'] = 'N'
            statstarQuestion.style.color = 'var(--primary-color)'
            statstarQuestion.style.cursor = 'pointer';
            
            var dynamicQuestion = document.getElementById(`dynamicQuestionCheckBox_${questionid}_${testid}`)
            if(dynamicQuestion){
                
                if(dynamicQuestion.checked == false){}
                else{
                    showSuccessMessage('This Question added in Dynamic Questions uncheck the question in Dynamic section');
                    staticQuestion_.checked = false
                }
            }

        }
        else{
            statstarQuestion.dataset['disable'] = 'Y'
            statstarQuestion.style.color = 'gray'
            statstarQuestion.style.cursor = 'not-allowed';

        }

    }

    questionCountChanger(TestId)

}


function questionCountChanger(TestId){

    var statQuesCount = 0
    var dynaQuesCount = 0
    var librariesLst = TestWithLibrariesAndQuestions[TestId]
    
    for(var library = 0; library < librariesLst.length; library++){

        if(librariesLst[library]['id'] == testsList[TestId]['paperlibraryid']){

            librariesLst[library]['papertype'] = ''
            var questionLst = librariesLst[library]['questionsList']
            for(var ques = 0; ques < questionLst.length; ques++){
                
                var statcheckElement = document.getElementById(`staticQuestionCheckBox_${questionLst[ques]['question_id']}_${TestId}`)
                
                if(statcheckElement){
                    if(statcheckElement.checked){
                        statQuesCount+=1
                    }
                }

                var dynacheckElement = document.getElementById(`dynamicQuestionCheckBox_${questionLst[ques]['question_id']}_${TestId}`)
                
                if(dynacheckElement){
                    if(dynacheckElement.checked){
                        dynaQuesCount+=1
                    }
                }
                
            }

            break

        }
        else{
            console.log('lubrary NOt FIND');
        }
    }

    var elementStat = document.getElementById(`static_questions_count_${TestId}`)
    if(elementStat){
        elementStat.innerText = statQuesCount
    }

    var elementDyn = document.getElementById(`dynamic_questions_count_${TestId}`)
    if(elementDyn){
        elementDyn.innerText = dynaQuesCount
    }

}


function createPaper(libraryid, testid, event) {
    return new Promise((resolve, reject) => {

        createNewPaper['staticQuestions'] = [];
        createNewPaper['event'] = 'useTemplate';
        createNewPaper['paperDetails'] = testsList[testid];
        createNewPaper['paperLibraryId'] = libraryid;
        createNewPaper['paperTitle'] = testsList[testid]['papertitle'];

        if (event === 'useTemplate') {
            var selectedQuestionsLst = TestWithLibrariesAndQuestions[testid];
            
            for (var ques = 0; ques < selectedQuestionsLst.length; ques++) {
                if (selectedQuestionsLst[ques]['id'] == libraryid) {
                    var libraryQuestioneList_ = selectedQuestionsLst[ques]['questionsList'];
                    
                    for (var i = 0; i < libraryQuestioneList_.length; i++) {
                        createNewPaper['staticQuestions'].push(libraryQuestioneList_[i]['question_id']);
                    }
                    
                    var final_data = {
                        "data": JSON.stringify(createNewPaper),
                        csrfmiddlewaretoken: CSRF_TOKEN,
                    };

                    // First AJAX call
                    $.post(CONFIG['acert'] + "/api/save-paper", final_data, function (res) {

                        if (res.statusCode === 0 && res.data) {
                            var data = res.data;
                            selectedPaper = data;

                            var dataObj = {
                                'createOrUpdate': 'update',
                                'createdPaperid': data['createdPaperid'],
                                'testId': testid,
                                'testName': null,
                                'promotPercentage': null,
                                'jdId': jdId,
                                'libraryId': libraryid
                            };

                            var final_data_jd = {
                                'data': JSON.stringify(dataObj),
                                csrfmiddlewaretoken: CSRF_TOKEN,
                            };

                            // Saving Paper id in hireline with this app 
                            $.post(CONFIG['portal'] + "/api/jd-add-or-update-test", final_data_jd, function (res) {
                                resolve(data); // Resolve the promise with the data after both calls
                            }).fail((error) => {
                                console.error('Error in second API call:', error);
                                reject(error); // Reject on second API call error
                            });

                        } else {
                            console.error('Error in first API call response:', res);
                            reject(new Error("Failed to create paper")); // Reject on first API call error
                        }
                    }).fail((error) => {
                        console.error('Error in first API call:', error);
                        reject(error); // Reject on first API call error
                    });

                    // Exit loop once the matching library ID is found
                    break;
                }
            }
        } else {
            console.error('Invalid event:', event);
            reject(new Error("Invalid event"));
        }
    });
}


function deleteTestModalOpen(testid) {

    if(JdStatus == 'D'){
        var testTilt =  document.getElementById('testTitle_'+testid).innerText
        document.getElementById('delectCancelBtn').hidden = false
        document.getElementById('deleteTestConformation').hidden = false
        document.getElementById('conformationForDelete').innerText =  'Are sure want to delete '+testTilt
        document.getElementById('deleteTestConformation').dataset['deletetestid'] = testid
        $('#modalToggle').modal('show')
        event.stopPropagation();
        TestWithLibrariesAndQuestions
    }
    else{
        document.getElementById('delectCancelBtn').hidden = true
        document.getElementById('deleteTestConformation').hidden = true
        document.getElementById('deleteCloseBtn').hidden = false
        document.getElementById('conformationForDelete').innerText =  "Can't delete any of this test"
        $('#modalToggle').modal('show')
    }
    
}


function deleteTest() {
    var deleteTestid = document.getElementById('deleteTestConformation').dataset['deletetestid'];

    if (deleteTestid) {
        var dataObj = {
            'deleteTestId' : parseInt(deleteTestid),
            'jdid': jdId
        };

        var final_data = {
            'data': JSON.stringify(dataObj),
            csrfmiddlewaretoken: CSRF_TOKEN,
        };

        $.post(CONFIG['portal'] + "/api/delete-test-injd", final_data, function (res) {
            if (res.statusCode == 0) {

                var data = res.data

                if(data['paperId']){

                    dataObj = {
                        'event':'paperStatus',
                        'paperId': data['paperId'],
                        'paperTitle': data['papertitle'],
                        'promotPercentage': ""
                    }
                    
                    var final_data = {
                        'data': JSON.stringify(dataObj),
                        csrfmiddlewaretoken: CSRF_TOKEN,
                    }
                    
                    $.post(CONFIG['acert'] + "/api/update-paperdetails", final_data, function (res) {

                    })
                }

                var testCardDetails = res.data

                // Find the element to remove
                var removeTestCard = document.getElementById(`${testCardDetails['testData']['papertype']}_${testCardDetails['testData']['id']}`);
                var testCardContainer = document.getElementById(`testCardSubContainer_${testCardDetails['testData']['id']}`);
                var removeQuestionsContainer = document.getElementById(`workFlowContainer_${testCardDetails['testData']['id']}`)

                var clickOnAnotherCard = false
                if ( removeTestCard.classList.contains('activeTestCars-interview-test') || removeTestCard.classList.contains('activeTestCars-coding-test') || removeTestCard.classList.contains('activeTestCars-screen-test')) {
                    clickOnAnotherCard = true;
                }
                
                // // Check if the element exists before removing it
                if (testCardContainer && removeQuestionsContainer) {
                    testCardContainer.innerHTML = ""
                    testCardContainer.remove()
                    // removeTestCard.parentNode.innerHTML = "" // Remove the element from the DOM
                    removeQuestionsContainer.innerHTML = ""
                    removeQuestionsContainer.remove()
                }

                if(clickOnAnotherCard){
                    if(testCardDetails['nextSelectTestId'] != 0){   
                        document.getElementById(`${testsList[testCardDetails['nextSelectTestId']]['papertype']}_${testsList[testCardDetails['nextSelectTestId']]['id']}`).click()
                    }
                }
                
                delete testsList[deleteTestid]

            }
        }).fail(function (error) {
            console.error("Paper delete failed:", error);
        });

        $('#modalToggle').modal('hide');
    }
}


// Interview panel
document.addEventListener('DOMContentLoaded', function () {
    function disableSelectedOptions() {
        var allSelects = document.getElementsByClassName('interviewer-select');
        
        Array.from(allSelects).forEach(function (select) {
            var selectedValue = select.value;
            
            Array.from(select.options).forEach(function (option) {
                if (option.value !== "" && option.value !== selectedValue) {
                    var isOptionSelected = Array.from(allSelects).some(function (otherSelect) {
                        return otherSelect !== select && otherSelect.value === option.value;
                    });
                    option.disabled = isOptionSelected;
                }
            });
        });
    }

    disableSelectedOptions();

    document.getElementById('addInterviewerButton').addEventListener('click', function () {
        var container = document.getElementById('interviewPanelContainer');
        var panelCount = container.getElementsByClassName('interview-panel').length;

        var newPanel = document.createElement('div');
        newPanel.classList.add('form-group', 'row', 'interview-panel');
        newPanel.id = 'panel_' + (panelCount + 1);

        var labelDiv = document.createElement('div');
        labelDiv.classList.add('col-xl-3', 'col-form-label');
        newPanel.appendChild(labelDiv);

        var newDiv = document.createElement('div');
        newDiv.classList.add('col-xl-6');

        var newSelect = document.createElement('select');
        newSelect.classList.add('custom-select', 'custom-select-sm', 'interviewer-select', 'form-select', 'my-2');
        newSelect.required = true;

        var defaultOption = document.createElement('option');
        defaultOption.value = '';
        defaultOption.disabled = true;
        defaultOption.selected = true;
        defaultOption.textContent = 'Select Interviewer';
        newSelect.appendChild(defaultOption);
        
        interviewersList.forEach(function (interviewer) {
            var option = document.createElement('option');
            option.value = interviewer.id;
            option.textContent = interviewer.name;
            newSelect.appendChild(option);
        });

        newDiv.appendChild(newSelect);
        newPanel.appendChild(newDiv);

        var buttonDiv = document.createElement('div');
        buttonDiv.classList.add('col-xl-2', 'd-flex', 'align-items-center');

        var removeButton = document.createElement('button');
        removeButton.type = 'button';
        removeButton.classList.add('btn', 'btn', 'remove-panel-button', 'interviewDelBtnBorder');
        removeButton.innerHTML = '<i class="far fa-trash-alt text-danger"></i>';
        removeButton.style.padding = '0.4375rem 1rem'

        removeButton.addEventListener('click', function () {
            container.removeChild(newPanel);
            disableSelectedOptions();
        });

        buttonDiv.appendChild(removeButton);
        newPanel.appendChild(buttonDiv);

        container.appendChild(newPanel);
        disableSelectedOptions();
    });

    Array.from(document.getElementsByClassName('remove-panel-button')).forEach(function (button) {
        button.addEventListener('click', function () {
            var panel = button.closest('.interview-panel');
            panel.parentNode.removeChild(panel);
            disableSelectedOptions();
        });
    });

    Array.from(document.getElementsByClassName('interviewer-select')).forEach(function (select) {
        select.addEventListener('change', disableSelectedOptions);
    });

    Array.from(document.getElementsByClassName('interviewer-select')).forEach(function (select) {
        select.querySelector('option[value=""]').disabled = true;
    });
});


function saveInterviewers(){
    if(jdId){
        var selectedInterviewersList = []
        var selectedInterviewersLst = document.getElementsByClassName('interviewer-select')

        for(var interviewer = 0; interviewer < selectedInterviewersLst.length; interviewer++ ){
            if(selectedInterviewersLst[interviewer].tagName == 'SELECT'){

                if (selectedInterviewersLst[interviewer].value){
                    selectedInterviewersList.push(selectedInterviewersLst[interviewer].value)
                }

            }
        }

        if(selectedInterviewersList.length > 0){

            totalinterviwersLst = selectedInterviewersList

            dataObj = {
                'interviwersLst' : selectedInterviewersList,
                'jdId'           : jdId
            }

            var final_data = {
                'data': JSON.stringify(dataObj),
                csrfmiddlewaretoken: CSRF_TOKEN,
            }

            // save paper id in jbdesc table 
            $.post(CONFIG['portal'] + "/api/save-interviewers-lst", final_data, function (res) {

                if(res.statusCode == 0){
                    totalinterviwersLst = res.data
                    $('#InterviewPanel').modal('hide');
                }

            })

        }
    }
}


function publishJd(){

    var testLst = Object.keys(testsList).length

    if(testLst >= 1){

        dataObj = {
            'jobDescriptionId' : jdId,
            'nextStatus_' : nextStatus
        }
        
        var final_data = {
            'data': JSON.stringify(dataObj),
            csrfmiddlewaretoken: CSRF_TOKEN,
        }
    
        // save paper id in jbdesc table 
        $.post(CONFIG['portal'] + "/api/jd-publish", final_data, function (res) {
    
            if(res.statusCode == 0){

                changeStatusInHtml(res.data['jdStatus_'])

                JdStatus = res.data['jdStatus_']

                if(res.data['noPaper'] == 'Y'){
                    // Show Modal
                    document.getElementById('PublishValidators').innerText = res.data['paperTitle']+' '+'Does not Select any Library.'
                    $('#JdPublishConformation').modal('hide')
                    $('#publishValidationModal').modal('show')
                }
                else{
    
                    dataObj = {
                        'data':res.data
                    }
                
                    var final_data = {
                        'data': JSON.stringify(dataObj),
                        csrfmiddlewaretoken: CSRF_TOKEN,
                    }
    
                    $.post(CONFIG['acert'] + "/api/update-brules", final_data, function (res) {
                    
                    });

                    if(JdStatus == 'A'){
                        showSuccessMessage('JD Published Successfully');
                    }
                    if(JdStatus == 'P'){
                        showSuccessMessage('JD Stopped Successfully');
                    }

                    // deleteTestValidation(JdStatus)
 
                    // if(JdStatus == 'A'){
                    //     showFailureMessage('JD ') 
                    // }

                    $('#JdPublishConformation').modal('hide')
    
                }
            }
    
        })
    }
    else{
        $('#JdPublishConformation').modal('hide')
        $('#jdPublishValidators').modal('show')
    }

}


function closeModals(){
    $('#publishValidationModal').modal('hide')
}


function openInterviewpPanel(){
    $('#InterviewPanel').modal('show')
}


// only allow when JD status "D"
// function deleteTestValidation(JdStatus__){
//     console.log(':::',JdStatus__);

//     document.getElementsByClassName('')

//     if(JdStatus__ == 'A'){

//     }

// }


function setUpInstructions(){
    document.getElementById('setupInstructions').hidden = false
}


// it update the star question state and status
function makeAsStarQuestion(questionId, TestId){

    var staticstarElement = document.getElementById(`staticstarQuestion_${questionId}_${TestId}`)

    // disable "N" means that question was in Paper
    // if star was disable "N" means NO then only we have to update or change state of the star
    if(staticstarElement.dataset['disable'] == 'N'){

        // un checked star
        if (staticstarElement.dataset['star'] == 'Y') { 
            staticstarElement.classList.remove('fas'); // remove filled star
            staticstarElement.classList.add('far'); // empty star
            staticstarElement.dataset['star'] = 'N';
        } 
        // checked star
        else {
            staticstarElement.classList.remove('far'); // remove empty star
            staticstarElement.classList.add('fas'); // filled star
            staticstarElement.dataset['star'] = 'Y'; 
        }

        dataObj = {
            'questionId'  : questionId,
            'testCardId'  : TestId,
            'staryesorno' : staticstarElement.dataset['star']
        }

        var final_data = {
            'data': JSON.stringify(dataObj),
            csrfmiddlewaretoken: CSRF_TOKEN
        }

        $.post(CONFIG['portal'] + "/api/make-star-question", final_data, function (res) {
            if (res.statusCode == 0) {
                
            }
        }).fail(function (error) {
            console.error("API request failed:", error);
        });
        
    }

}


function enableOrDisableHold() {
    var testHoldElement = document.getElementById('testHold');
    var holdContainer = $('#holdInputContainer'); // Use jQuery selector for holdContainer
    var holdInputInfo = document.getElementById('holdInfo');
    var holdPercentageInputElement = document.getElementById('holdPercentage');
    var promotePercentageValueElement = document.getElementById('promot_level')

    // if(!holdPercentageInputElement.value){
        var reducedValue = 50
        if(promotePercentageValueElement.value){
            reducedValue = promotePercentageValueElement.value - (promotePercentageValueElement.value * (20 / 100));
        }
    // }

    if (testHoldElement.checked) {
        holdContainer.fadeIn(); // Show the container with fade-in effect
        holdInputInfo.innerText = 'Below the Hold percentage candidate will be rejected';
        holdPercentageInputElement.value = reducedValue
    } else {
        holdContainer.fadeOut(); // Hide the container with fade-out effect
        holdInputInfo.innerText = 'Below the Promote percentage candidate will be rejected';
    }
}