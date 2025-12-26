var perviousSelectedTest = null
var screeningBackgroundColor = '#efebfd'; var codingBackgroundColor = '#defaeb'; var interviewBackgroundColor = '#e2ebfd'
var screenMainColor = '#8763ee'; var codingMainColor = '#00d462'; var interviewMainColor = '#1f68f3';

// it contains paper id job id company id paper type promote percentage
var testsList = {}

var testCreateOrUpdate // store "create" or "update", if it create, it create a new test or update , it update the existing test 
var cureentTestId
var instialSelectTest = []
var testsList_ = []
var allBasicScreeningQuestions = []
const loader = document.getElementById('candidates-loader');
// var TestWithLibrariesAndQuestions = {}
var JdStatus = ''
var nextStatus
var totalinterviwersLst

// we store list of all screening basic questions
var screeningBasicQuestionsList = []

// work selecting skills and topics and subtopics and hidding and unhidding

var skillsClickesTracker = {}

// using for skills selecting or topic selecting or subtopic
// var createTestCard = true

// skills and topics and subtopic
var skillsTopicSubtopics 


// adding all questions in a seprate list's depends on the subtopic ids
var allTestsQuestions = {};

// this variable containes selected question ids with html
var questionHasToBeSelected = []

var DynamicQuesCount

var dynamicQuestionCountInputValueBackup = 0

// var jdBasedQuesFromPaper


$(document).ready(function () {
    Promise.all([
        workFlowData(), // it has to call first because it get all test data and create html after skill, topic, subtopics are added in to that html
        getSkills(),
    ])
})


// sending skills to acert for topics and subtopics
function getSkills() {

    // Sending Skills List And Tests with paper details

    var skills = {
        data: skillLst,  // Pass the actual list of skills
        testData: workFlowDetails,  // Pass the actual list of skills
        companyId : companyId
    };

    // Send as JSON using $.ajax
    $.ajax({
        url: CONFIG['acert'] + "/api/getTopicAndSubtopicAndQuestions",
        type: "POST",
        contentType: "application/json", // Send the request as JSON
        data: JSON.stringify(skills),    // Properly serialize the data
        headers: {
            "X-CSRFToken": CSRF_TOKEN    // Include the CSRF token in headers
        },
        success: function (res) {
            if (res.statusCode == 0) {

                skillsTopicSubtopics = res.data['skillsList']
                // console.log('skillsTopicSubtopics',skillsTopicSubtopics)

                DynamicQuesCount = res.data['paperSubtopicComplexityQuestionsCount']

                var papersMarksAndQues = res.data['papersMarksAndQuestions']

                // jdBasedQuesFromPaper = res.data['jdBasedQues']

                for (var key in workFlowDetails) {
                    
                    if (workFlowDetails.hasOwnProperty(key)) {
                        
                        var workflowData = workFlowDetails[key]; // Access the value by the key
                        console.log('workflowData',workflowData);
                        paper_id = workflowData.paperid
                        
                        // this function call when page loads or page referesh's.
                        // it create html with skills with topic with subtopic 
                        skillsListShowInHtml(workflowData.id, res.data['skillsList'], workflowData.papertype, DynamicQuesCount, paper_id);

                        if(testsList[workflowData.id]['paperid']) {
                            fillDynamicQuestionsInputField(workflowData.id,DynamicQuesCount[testsList[workflowData.id]['paperid']])
                        }
                    }
                    else{
                        console.log('key condition faill');
                    }
                }

                paperQuestionsCountAndMarksSetInHTML(papersMarksAndQues)

                console.log('testsList',testsList)

            }
        },
        error: function (jqXHR, textStatus, errorThrown) {
            console.error("Request failed:", textStatus, errorThrown);
        }
    });
}



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
                
                if(res.data['workFlowData'].length == 0){
                    loader.style.display = 'none'
                }
                
                // // it Creates Test Card
                // createTest(res.data['workFlowData'],'edit')
                
                // // // it Create Questions Container for each Test
                // createWorkFlowContainer(res.data['workFlowData'])

                // // // change status in html
                // changeStatusInHtml(res.data['jdStatus'])


                // // Execute both functions in parallel and handle results
                Promise.all([
                    // it Creates Test Card
                    createTest(res.data['workFlowData'], 'edit'),

                    // it Create Questions Container for each Test card
                    loopThroughWorkFlowData(res.data['workFlowData'],res.data['skillsLst']),

                    // change status in html
                    changeStatusInHtml(res.data['jdStatus'])
                ])
                .then(() => {
                    // console.log("Both functions executed successfully.");
                })
                .catch((error) => {
                    // console.error("An error occurred while executing functions:", error);
                });
                
                // Assigning Interviwers 
                totalinterviwersLst = res.data['selectedJDInterviewers']
                
                // assign the Jd Status
                JdStatus = res.data['jdStatus']

            }
        }

    })

}


function getAllBasicScreeningQuestions(testId) {
    return new Promise((resolve, reject) => {
        const getQuestions = { jd_id: jdId , test_id: testId};

        var final_data = {
            "data": JSON.stringify(getQuestions),
            csrfmiddlewaretoken: CSRF_TOKEN,
        };

        $.post(CONFIG['portal'] + "/api/get-jd-screening-questions", final_data, function(res) {
            console.log('res',res)
            if (res.statusCode == 0 && res.data) {
                resolve(res.data); // Resolve with the data

                // stop the loader, by display none
                loader.style.display = 'none';

            } else {
                reject("Failed to fetch questions");
                // stop the loader, by display none
                loader.style.display = 'none';
            }
        }).fail(function(error) {
            reject(error); // Reject on error
        });
    });
}



// when we refresh the page it takes data from the workflow and loops creates the all test cards
//  create cards by calling this function 
function createTest(data){
    if(data.length > 0){
        for(var test = 0; test < data.length; test++){
            addTestCardToShow(data[test]['papertitle'], data[test]['promot'],data[test]['papertype'],data[test])  
            
            var key_ = data[test]['id']
            testsList[[key_]] =  data[test]
            testsList_.push(key_)

        }
    }
}


// loop through work flow data
function loopThroughWorkFlowData(data){
    if(data.length > 0){

        for(var containerCount = 0; containerCount < data.length; containerCount++){
            
            skillsClickesTracker = {
                [`previousSelectedSkill_${data[containerCount]['id']}`]: null,
                [`previousSelectedTopicId_${data[containerCount]['id']}`]: null,
                [`previousSelectedTopicContainerId_${data[containerCount]['id']}`]: null,
                [`previousSelectedSubTopicId_${data[containerCount]['id']}`]: null,
                [`previousSelectedSubTopicContainerId_${data[containerCount]['id']}`]: null,
                [`previousSelectedSubTopicQuestionsContainerId_${data[containerCount]['id']}`]: null
            };

            var testId = data[containerCount]['id']
            var paperType  = data[containerCount]['papertype']
            var PaperTitle = data[containerCount]['papertitle']
            var TestData = data[containerCount]
            var container = 'hide'
            var initalTestCard = false
            var skillsList

            if(containerCount == 0){
                container = 'show'
                initalTestCard = true
            }

            // it create test card questions container.
            TestCardQuestionsMainContainers(testId,paperType, PaperTitle, container, initalTestCard, TestData)

        }

    }

}


// It creates test card questions container and puts it in a single container
function TestCardQuestionsMainContainers(testId, paperType, PaperTitle, showOrHide, initalTestCard, TestData) {

    var mainContainer = document.getElementById('TestCardQuestionsContainersList');
    var workFlowContainer = document.createElement('div');
    workFlowContainer.id = 'TestContainer_' + testId;
    workFlowContainer.style.paddingBottom = '1rem';

    // Create the test card header element
    var testCardHeaderElement = document.createElement('div');
    testCardHeaderElement.id = `testCardQuestionsContainerHeader_${testId}`;

    // Hide the workflow container by default
    workFlowContainer.hidden = true;

    // Show the container if showOrHide is not 'hide'
    if (showOrHide !== 'hide') {
        workFlowContainer.hidden = false;
    }

    // If it's an initial test card, trigger a click on the corresponding element
    if (initalTestCard == true) {
        var testCard = document.getElementById(paperType + '_' + testId);
        if (testCard) { // Check for the card element
            testCard.click();
        }
    }

    // Create the test card questions container header
    var firstContainer = TestCardQuestionContainerHeader(testId, paperType, PaperTitle);
    testCardHeaderElement.innerHTML = firstContainer;

    // Add screening tabs if the paper type is 'S'
    if (paperType == 'S') {
        var screeningTabsContainer = screeningTabs(testId);
        testCardHeaderElement.innerHTML += screeningTabsContainer;
    }
    //  Keep your existing header buttons same
    if (paperType === 'S') {
        testCardHeaderElement.innerHTML += `
        
        <div class="mt-3 mb-2 d-flex justify-content-between align-items-center">
            <button class="btn btn-outline-primary"
                    onclick="previewQuestions(${testId}, 'S')"
                    data-bs-toggle="tooltip"
                    data-bs-placement="right"
                    title="If any changes are made, please save and preview">
                <i class="fas fa-eye"></i> Preview 
            </button>

            <input type="text"
                class="form-control jd-search-input"
                placeholder="Search questions..."
                data-testid="${testId}"
                onkeyup="searchJDQuestions(this)"
                style="max-width:300px;">
        </div>
    `;
    }
    if (paperType === 'E') {
        testCardHeaderElement.innerHTML += `
        <div class="mt-3 mb-2 d-flex justify-content-between align-items-center">
            <button class="btn btn-outline-primary"
                    onclick="previewQuestions(${testId}, 'E')"
                    data-bs-toggle="tooltip"
                    data-bs-placement="right"
                    title="If any changes are made, please save and preview">
                <i class="fas fa-eye"></i> Preview 
            </button>
            <input type="text"
                class="form-control jd-search-input"
                placeholder="Search questions..."
                data-testid="${testId}"
                onkeyup="searchJDQuestions(this)"
                style="max-width:300px;">
        </dd-flex>
    `;
    }
    if (paperType === 'I') {
        testCardHeaderElement.innerHTML += `
        <div class="mt-3 mb-2 d-flex justify-content-between align-items-center">
            <button class="btn btn-outline-primary"
                    onclick="previewQuestions(${testId}, 'I')"
                    data-bs-toggle="tooltip"
                    data-bs-placement="right"
                    title="If any changes are made, please save and preview">
                <i class="fas fa-eye"></i> Preview 
            </button>
            <input type="text"
                class="form-control jd-search-input"
                placeholder="Search questions..."
                data-testid="${testId}"
                onkeyup="searchJDQuestions(this)"
                style="max-width:300px;">
        </div>
    `;
    }
   
    // Append the header element to the workflow container
    workFlowContainer.appendChild(testCardHeaderElement);

    // Append the workflow container to the main container
    mainContainer.appendChild(workFlowContainer);
    initTooltips();
    if (paperType == 'S') {
        var dynamicQuestionsContainerToHide = document.getElementById(`dynamicQuestionsContainer_${testId}`)
        // hide the dynamic questions count
        if(dynamicQuestionsContainerToHide){
            dynamicQuestionsContainerToHide.hidden = true
        }
        else{
            console.log(" can't hide the dynamic questions container ");
        }
    }

    if(paperType == 'S' || paperType == 'I'){

        var createQuestionContainer = createNewQuestionContainer(testId, paperType);
        testCardHeaderElement.innerHTML += createQuestionContainer;

    }
    var instructionsContainer = document.getElementById('instructionsContainer');
    if (instructionsContainer) {
        instructionsContainer.hidden = true;
    }

}


// test card header test name paper data & save & create New question ETC..... 
function TestCardQuestionContainerHeader(testId,PaperType,PaperTitle){

    var customHiddelabels = ''
    var showInterviewTest = 'hidden'
    var screeningCustmClass = ""
    var screeningStaticQuestionsCount = ''

    var createCustomQuestion = ''
    if(PaperType != 'E'){
        // createCustomQuestion = `<button id="CreateCustomQuestion_${testId}" class="btn btn-primary btn-custom-margin-left"> Create Question </button>`
    }
    else{
        createCustomQuestion = ''
    }

    if(PaperType == 'I'){
        showInterviewTest = ""
        customHiddelabels = 'hidden'
    }
    else{
        showInterviewTest = 'hidden'
    }

    if(PaperType == 'S'){
        screeningCustmClass = `screeningTestId_${testId}`
        screeningStaticQuestionsCount = `screeningStaticQuestionsCount_${testId}`
    }
    else{
        screeningCustmClass = ''
        screeningStaticQuestionsCount = ''
    }
    
    
    var wholeContainer = `<div class="testCardQuestionsHeadingContainer">
        <h4 id="Testtitle_${testId}"  class="m-0">${PaperTitle}</h4>
    
        <div class="testCardQuestionsFirstContainer-first-child">

            <div id="paperWeightage_${testId}" ${customHiddelabels}>Weightage - 
                <span id="TestWeightage_${testId}" class="${screeningCustmClass}"> 0 </span> 
            </div>

            <div id="staticQuestionsCountainer_${testId}" class="text-align-custom-left-margin" ${customHiddelabels}>
                <span class="" style="font-weight: 700;">Questions</span> Static - 
                <span id="StaticQuestionsCount_${testId}" class="${screeningStaticQuestionsCount}"> 0 </span>
            </div>

            
            <div id="dynamicQuestionsContainer_${testId}" class="text-align-custom-left-margin" ${customHiddelabels}>
            Dynamic - <span id="DynamicQuestionsCount_${testId}"> 0 </span>
            </div>

            <div id="InterviewQuestionsContainer_${testId}" class="text-align-custom-left-margin" ${showInterviewTest}>
                <span style="font-weight: 700;">  Questions </span> - <span id="InterviewQuestionsCount_${testId}"> 0 </span>
            </div>

            <button id="save_${testId}" class="btn btn-primary btn-custom-margin-left" data-testid="${testId}" onclick="savePaper(this.id)"> Save </button>
            <button id="preview_${testId}" class="btn btn-primary btn-custom-margin-left" hidden> Preview </button>
            ${createCustomQuestion}

        </div>
    </div>`
    
    return wholeContainer

}


// screening Tabs and screening Questions container for each tab
function screeningTabs(testId){
    var tabs = `<div class="screeningTabsContainer" id="screeningTabsContainer_${testId}">
        <div class="switch-btw-screening">
          <div id="screeningTab_1_${testId}" class="screeningTestTab active-screeningTab" data-screeningtype="basic" onclick="activeScreeningTab(this)">JD Screening</div>
          <div id="screeningTab_2_${testId}" class="screeningTestTab m-0" data-screeningtype="knowledge" onclick="activeScreeningTab(this)">JD Knowledge test</div>
        </div>
    </div>
    `
    return tabs
}


// Show skills, topics, and subtopics in HTML
function skillsListShowInHtml(testId, skillData, PaperType, DynamicQuesCount, paper_id) {

    let skillsHtml = "";
    let skillsTopicsHtml = "";
    let skillsSubTopicHtml = "";

    // Creating Container for skills list and appending to the HTML
    let testContainerElement = document.getElementById(`testCardQuestionsContainerHeader_${testId}`);

    var skillsAndTopicsAndSubtopicsContainer = document.createElement('div')
    skillsAndTopicsAndSubtopicsContainer.id = `skillsAndTopicsAndSubtopicsContainer_${testId}`

    if(testContainerElement){
        testContainerElement.appendChild(skillsAndTopicsAndSubtopicsContainer)
    }

    var skillsListHtml = `
        <div class="skillsListMainContainer">
            <h5 class="p-clr">Skills</h5>
            <div class="skillsList" id="skillsList_${testId}">
            </div>
        </div>
        <div class="customHr"> </div>
        `;

    // Appended to the DOM HTML
    skillsAndTopicsAndSubtopicsContainer.innerHTML += skillsListHtml;
    
    if (skillData) {
         // Sort skills alphabetically
        skillData.sort((a, b) => (a.skill || "").localeCompare(b.skill || "", undefined, { sensitivity: "base" }));

        // Sort topics and subtopics alphabetically
        skillData.forEach(skill => {
            if (Array.isArray(skill.skillTopics)) {
                skill.skillTopics.sort((a, b) => (a.topicName || "").localeCompare(b.topicName || "", undefined, { sensitivity: "base" }));
                skill.skillTopics.forEach(topic => {
                    if (Array.isArray(topic.subTopics)) {
                        topic.subTopics.sort((a, b) => (a.subTopicName || "").localeCompare(b.subTopicName || "", undefined, { sensitivity: "base" }));
                    }
                });
            }
        });
        
        // Loop through skills
        for (let skill_ = 0; skill_ < skillData.length; skill_++) {
            let skillName = skillData[skill_]["skill"];
            let skillId = skillData[skill_]["skillId"];
            let skillTopics = skillData[skill_]["skillTopics"];

            // Adding each skill to the skill list
            if(skillId == undefined || skillId == null || skillTopics.length == 0){
                skillsHtml = `<button 
                            class="no-data-skill skill"
                            id="Skill_${skillId}_Test_id_${testId}"
                            onclick="showskillOrTopicOrSubtopicOrQuestions(this.id)" 
                            data-type="skill" 
                            data-data="N" 
                            title="Does not have any questions for this skill"
                            data-skillid="${skillId}"
                            data-testid="${testId}"
                            >${skillName}</button>`;
            }
            else{
                skillsHtml = `<button 
                            class="skillItems skill"
                            id="Skill_${skillId}_Test_id_${testId}"
                            onclick="showskillOrTopicOrSubtopicOrQuestions(this.id)" 
                            data-type="skill" 
                            data-data="Y" 
                            data-skillid="${skillId}"
                            data-testid="${testId}"
                            >${skillName}</button>`;
            }

            document.getElementById(`skillsList_${testId}`).innerHTML += skillsHtml;

            var topicsListHtml = `
                <div id="SkillTopicContainer_${skillId}_Test_${testId}" class="skillsTopicsMainContainer" hidden>
                    <h5 class="p-clr">Topics</h5>
                    <div class="skillsListTopicsList" id="TopicsList_${skillId}_testId_${testId}">
                    </div>
                    <div class="customHr"> </div>
                </div>`;

            skillsAndTopicsAndSubtopicsContainer.innerHTML += topicsListHtml;

            // Looping the skill Topics
            for (let topic_ = 0; topic_ < skillTopics.length; topic_++) {
                let topicName = skillTopics[topic_]["topicName"];
                let topicId = skillTopics[topic_]["id"];
                let topicScreening = skillTopics[topic_]["screening"];
                let topicCoding = skillTopics[topic_]["coding"];
                let topicInterview = skillTopics[topic_]["interview"];

                // Conditions for adding topics based on PaperType
                skillsTopicsHtml = `<button class="skillItems"
                                        id="Skill_${skillId}_Topic_${topicId}_Test_id_${testId}"
                                        onclick="showskillOrTopicOrSubtopicOrQuestions(this.id)" 
                                        data-type="topic" 
                                        data-skillid="${skillId}"
                                        data-topicid="${topicId}"
                                        data-testid="${testId}" 
                                        >${topicName}</button>`;


                if (skillsTopicsHtml) {
                    // Append topics to the respective skill container.
                    document.getElementById(`TopicsList_${skillId}_testId_${testId}`).innerHTML += skillsTopicsHtml;
                }

                var subTopicsListHtml = `
                    <div id="SkillSubTopicContainer_${topicId}_Skill_${skillId}_Test_${testId}" class="skillsSubTopicsMainContainer" hidden>
                        <h5 class="p-clr">Subtopics</h5>
                        <div class="skillsList" id="SubTopicsList_${topicId}_testId_${testId}">
                        </div>
                        <hr class="skillsAndQuestionsContainerSeprater">
                    </div>`;
                skillsAndTopicsAndSubtopicsContainer.innerHTML += subTopicsListHtml;

                // Subtopics logic can be added here if required, as in your commented code
                // Uncomment if needed for dynamic subtopic handling
                let subTopics = skillTopics[topic_]["subTopics"];

                for (let subTopic_ = 0; subTopic_ < subTopics.length; subTopic_++) {
                    let subTopicName = subTopics[subTopic_]["subTopicName"];
                    let subTopicId = subTopics[subTopic_]["id"];
                    let subTopicScreening = subTopics[subTopic_]["screening"];
                    let subTopicCoding = subTopics[subTopic_]["coding"];
                    let subTopicInterview = subTopics[subTopic_]["interview"];

                    let subtopicQuestionsList = subTopics[subTopic_]["questionsList"];

                    skillsSubTopicHtml = `<button class="skillItems" 
                                            id="Skill_${skillId}_Topic_${topicId}_subTopic_${subTopicId}_Test_id_${testId}"
                                            onclick="showskillOrTopicOrSubtopicOrQuestions(this.id)" 
                                            data-type="subtopic"
                                            data-subtopicid="${subTopicId}"
                                            data-topicid="${topicId}"
                                            data-testid="${testId}" 
                                            >
                                            ${subTopicName}</button>`;

                    if (skillsSubTopicHtml) {
                        // Append topics to the respective skill container.
                        document.getElementById(`SubTopicsList_${topicId}_testId_${testId}`).innerHTML += skillsSubTopicHtml;
                    }

                    // creating the questions container for each subtopic , it contains subtopic related questions.  
                    var subtopicQuestionsMainContainer = document.createElement('div')
                    subtopicQuestionsMainContainer.id = `SubTopicQuestionsContainer_${subTopicId}_test_${testId}`

                    var complexitiesHtmlList = createAQuestion(skillId ,topicId , subTopicId , subtopicQuestionsList , testId, PaperType, paper_id)

                    for (let complexityItem = 0; complexityItem < complexitiesHtmlList.length; complexityItem++) {
                        let complexityElement = complexitiesHtmlList[complexityItem];
                        
                        if(complexityElement){
                            subtopicQuestionsMainContainer.appendChild(complexityElement) 
                        }

                        subtopicQuestionsMainContainer.hidden = true
                        
                        skillsAndTopicsAndSubtopicsContainer.appendChild(subtopicQuestionsMainContainer)

                    }
                
                }

            }

            // Reset HTML for next skill
            skillsTopicsHtml = "";
            skillsSubTopicHtml = "";

            // Apply a scrollbar to the container
            // addPerfectScrollbarToDynamicElement(testId);
        }
        
    }

    if(PaperType == 'S'){

        skillsAndTopicsAndSubtopicsContainer.hidden = true
        var screeningBasicElementContainer = document.createElement('div')
        screeningBasicElementContainer.id = `basicScreeningContainer_${testId}`
        testContainerElement.append(screeningBasicElementContainer);

        // this function get the data from another function and creates the html with question and add that html in to the webapge.
        genrateHtmlWithScreeningBasicQuestion(testId)
        
    }
    else{
        loader.style.display = 'none';
    }
    
    document.getElementById(`TestContainer_${testId}`).insertAdjacentHTML('beforeend', `
        <div style="display:flex; justify-content:flex-end; margin-top:10px;">
            <button id="save_${testId}" class="btn btn-primary btn-custom-margin-left" data-testid="${testId}" onclick="savePaper(this.id)"> Save </button>
        </div>
    `);
    
    questionCheckAsSelected()

    clickOnFirstSkill(testId)

    
}



function createAQuestion( skill_Id, topicId, subTopicId, quesData, test_Id, PaperType_, paper_id) {

    console.log('paper_id',paper_id)

    var complexityWiseQuestions = {
                                    'verylow'  : [],
                                    'low'      : [],
                                    'medium'   : [],
                                    'high'     : [],
                                    'veryhigh' : []
                                }

    for (let question_ = 0; question_ < quesData.length; question_++) {

        var ques = quesData[question_]


        // coding paper
        if(PaperType_ == 'E'){
            // paper types
            if(ques['questionType'] == 'C' || ques['questionType'] == 'R'){

                if(ques['questionComplexity'] == 1){
                    complexityWiseQuestions['verylow'].push(ques)
                }

                if(ques['questionComplexity'] == 2){
                    complexityWiseQuestions['low'].push(ques)
                }

                if(ques['questionComplexity'] == 3){
                    complexityWiseQuestions['medium'].push(ques)
                }

                if(ques['questionComplexity'] == 4){
                    complexityWiseQuestions['high'].push(ques)
                }

                if(ques['questionComplexity'] == 5){
                    complexityWiseQuestions['veryhigh'].push(ques)
                }

            }
        }
        // screening paper
        else if(PaperType_ == 'S'){
            // questions type
            if(ques['questionType'] == 'M' || ques['questionType'] == 'B' || ques['questionType'] == 'P' || ques['questionType'] == 'A' || ques['questionType'] == 'V'){

                if(ques['questionComplexity'] == 1){
                    complexityWiseQuestions['verylow'].push(ques)
                }

                if(ques['questionComplexity'] == 2){
                    complexityWiseQuestions['low'].push(ques)
                }

                if(ques['questionComplexity'] == 3){
                    complexityWiseQuestions['medium'].push(ques)
                }

                if(ques['questionComplexity'] == 4){
                    complexityWiseQuestions['high'].push(ques)
                }

                if(ques['questionComplexity'] == 5){
                    complexityWiseQuestions['veryhigh'].push(ques)
                }

            }
        }
        // interview test
        else if(PaperType_ == 'I'){
            // interview questions type
            if(ques['questionType'] == 'I'){

                if(ques['questionComplexity'] == 1){
                    complexityWiseQuestions['verylow'].push(ques)
                }

                if(ques['questionComplexity'] == 2){
                    complexityWiseQuestions['low'].push(ques)
                }

                if(ques['questionComplexity'] == 3){
                    complexityWiseQuestions['medium'].push(ques)
                }

                if(ques['questionComplexity'] == 4){
                    complexityWiseQuestions['high'].push(ques)
                }

                if(ques['questionComplexity'] == 5){
                    complexityWiseQuestions['veryhigh'].push(ques)
                }
                
            }
        }

    }

    var complexitysHtmlList = []
    var complexityHtml

    if(complexityWiseQuestions['verylow'].length > 0 ){
        complexityHtml = createComplexityQuestionsContainer(complexityWiseQuestions['verylow'], skill_Id, topicId, subTopicId, test_Id, PaperType_, 'verylow',paper_id)
        complexitysHtmlList.push(complexityHtml)
    }

    if(complexityWiseQuestions['low'].length > 0){
        complexityHtml = createComplexityQuestionsContainer(complexityWiseQuestions['low'], skill_Id, topicId, subTopicId, test_Id, PaperType_, 'low', paper_id)
        complexitysHtmlList.push(complexityHtml)
    }

    if(complexityWiseQuestions['medium'].length > 0){
        complexityHtml = createComplexityQuestionsContainer(complexityWiseQuestions['medium'], skill_Id, topicId, subTopicId, test_Id, PaperType_, 'medium', paper_id)
        complexitysHtmlList.push(complexityHtml)
    }

    if(complexityWiseQuestions['high'].length > 0){
        complexityHtml = createComplexityQuestionsContainer(complexityWiseQuestions['high'], skill_Id, topicId, subTopicId, test_Id, PaperType_, 'high', paper_id)
        complexitysHtmlList.push(complexityHtml)
    }

    if(complexityWiseQuestions['veryhigh'].length > 0){
        complexityHtml = createComplexityQuestionsContainer(complexityWiseQuestions['veryhigh'], skill_Id, topicId, subTopicId, test_Id, PaperType_, 'veryhigh', paper_id)
        complexitysHtmlList.push(complexityHtml)
    }

    return complexitysHtmlList
    
}


// it create complexity container for each subtopic it create low , verylow, medium, hard , veryhard complexity container and put in html
function createComplexityQuestionsContainer(complexityWiseQuestions, skill_Id, topicId, subTopicId, test_Id, PaperType_, complexityType, paper_id){
    // console.log('test_Id',test_Id)
    console.log('complexityWiseQuestions',complexityWiseQuestions)
    var fndFirstQuestionComplexity
    var complexityTxt
    var dynamicId
    var ComplexityTitles

    if(complexityWiseQuestions.length > 0){
        fndFirstQuestionComplexity = complexityWiseQuestions[0]['questionComplexity']
    }

    if(fndFirstQuestionComplexity == 1){
        complexityTxt = 'veryLow'
        ComplexityTitles = 'Complexity - Beginner'
    }

    if(fndFirstQuestionComplexity == 2){
        complexityTxt = 'low'
        ComplexityTitles = 'Complexity - Intermediate'
    }

    if(fndFirstQuestionComplexity == 3){
        complexityTxt = 'medium'
        ComplexityTitles = 'Complexity - Moderate'
    }

    if(fndFirstQuestionComplexity == 4){
        complexityTxt = 'high'
        ComplexityTitles = 'Complexity - Advanced'
    }

    if(fndFirstQuestionComplexity == 5){
        complexityTxt = 'veryHigh'
        ComplexityTitles = 'Complexity - Expert'
    }

    // create complexity container section.
    var complexityMainContainer = document.createElement('div');
    complexityMainContainer.id = `complexitySubTopicQuestions_${subTopicId}_testId_${test_Id}`;
    complexityMainContainer.dataset['complexitytype'] = complexityType
    complexityMainContainer.classList.add('complexityMainContainerCls')

    // // create complexity heading & Dynamic Questions count with input
    var complexiytHeaderContainer = document.createElement('div');
    complexiytHeaderContainer.classList.add('complexityContainerHeaderCls')

    var complexityHeading = document.createElement('h5');
    complexityHeading.classList.add('m-0')
    complexityHeading.innerText = ComplexityTitles; 
    
    // // Add a suitable text for the header
    var DynamicInoutTitle = document.createElement('h5')
    DynamicInoutTitle.classList.add('dynamicinptLabel')
    DynamicInoutTitle.innerText = 'Dynamic Questions count'

    var complexityDynamicInput = document.createElement('input');
    complexityDynamicInput.classList.add('dynamicInpt', 'form-control')
    complexityDynamicInput.id = `DynamicInput_TestId_${test_Id}_subTopic_${subTopicId}_complex_${complexityTxt}`;  // Set appropriate input type
    complexityDynamicInput.type = "number";  // Set appropriate input type
    complexityDynamicInput.min="0"
    complexityDynamicInput.dataset['complexitytype'] = complexityTxt;  // Set appropriate input type
    complexityDynamicInput.dataset['testid'] = test_Id; 
    complexityDynamicInput.dataset['skillid'] = skill_Id; 
    complexityDynamicInput.dataset['topicid'] = topicId; 
    complexityDynamicInput.dataset['subtopicid'] = subTopicId;
    complexityDynamicInput.dataset['paperid'] = paper_id
    // complexityDynamicInput.setAttribute(
    //     'onkeyup',
    //     `dynamicQuestionscountSave(this.id)`
    // );
    complexityDynamicInput.setAttribute(
        'onchange',
        `dynamicQuestionscountSave(this.id)`
    );

    complexityDynamicInput.setAttribute(
        'onmouseover',
        `DynamicInputValueBackUp(this.id)`
    );


    var dynamicInputLabelContainer = document.createElement('div')
    dynamicInputLabelContainer.classList.add('complexityDynamicContainer')
    dynamicInputLabelContainer.id = `complexityDynamicContainer_subtopicId_${subTopicId}_testId_${test_Id}`
    dynamicInputLabelContainer.dataset['']

    // if there is only one question in a complexity do not show the dynamic container 
    if(complexityWiseQuestions.length == 1){
        dynamicInputLabelContainer.hidden = true
    }

    dynamicInputLabelContainer.append(DynamicInoutTitle , complexityDynamicInput)

    complexiytHeaderContainer.append(complexityHeading, dynamicInputLabelContainer);
    
    var complexiytQuestionTypeLabels = document.createElement('div');
    complexiytQuestionTypeLabels.classList.add('questionTypeLabels')
    var questionTypeLabelStatic = document.createElement('h5')
    var questionTypeLabelDynamic = document.createElement('h5')

    questionTypeLabelStatic.classList.add('qStaticLabel')
    questionTypeLabelDynamic.classList.add('qDynamicLabel')

    questionTypeLabelStatic.innerText = 'Static'
    questionTypeLabelDynamic.innerText = 'Dynamic'
    if(PaperType_ == 'I'){
        questionTypeLabelDynamic.hidden = true
    }

    complexiytQuestionTypeLabels.append(questionTypeLabelStatic,questionTypeLabelDynamic)

    complexityMainContainer.append(complexiytHeaderContainer, complexiytQuestionTypeLabels);

    // // create questions container
    var questionsContainer = document.createElement('ol');

    for (let question_ = 0; question_ < complexityWiseQuestions.length; question_++) {
        
        let ques = complexityWiseQuestions[question_];
        
        // from here===================================
        
        var questionContainer = document.createElement('div');
        questionContainer.classList.add('customQuestionContainer')
        questionContainer.id = `QuestionContainerId_${ques['questionId']}`

        var questionElement = document.createElement('li');
        questionElement.id = `question_id_${ques['questionId']}`
        // questionElement.innerText = ques['question'].replace(/\\u[0-9A-Fa-f]{4}/g, '').replace(/\s+/g, ' ');  // Assuming ques is an object with 'question' key
        questionElement.innerText = ques['question']
        let questionMarks = ques['marks']

        let firstInpt = document.createElement('input');
        firstInpt.type = 'checkbox';  // Assuming you want checkboxes
        firstInpt.classList.add('form-check-input','mx-4')
        firstInpt.id = `questionId_${ques['questionId']}_${test_Id}_S`
        firstInpt.dataset['qid'] = ques['questionId']
        firstInpt.dataset['testid'] = test_Id
        firstInpt.dataset['skill'] = skill_Id
        firstInpt.dataset['topic'] = topicId
        firstInpt.dataset['subtopic'] = subTopicId
        firstInpt.dataset['marks'] = questionMarks
        firstInpt.dataset['complexity'] = complexityType
        firstInpt.dataset['type'] = 'S'
        firstInpt.dataset['paperid'] = paper_id
        firstInpt.setAttribute(
            'onclick',
            `addQuestionsToList(${ques['questionId']},this.id,${test_Id})`
        );

        // Another checkbox
        let secondInpt = document.createElement('input');
        secondInpt.type = 'checkbox'; 
        secondInpt.classList.add('form-check-input','mx-4','dynamic-custom-checkbox')
        secondInpt.id = `questionId_${ques['questionId']}_${test_Id}_D`
        secondInpt.dataset['qid'] = ques['questionId']
        secondInpt.dataset['testid'] = test_Id
        secondInpt.dataset['skill'] = skill_Id
        secondInpt.dataset['topic'] = topicId
        secondInpt.dataset['subtopic'] = subTopicId
        secondInpt.dataset['marks'] = questionMarks
        secondInpt.dataset['complexity'] = complexityType
        secondInpt.dataset['type'] = 'D'
        secondInpt.dataset['paperid'] = paper_id
        secondInpt.setAttribute(
            'onclick',
            `addQuestionsToList(${ques['questionId']},this.id,${test_Id})`
        );

        if(complexityWiseQuestions.length == 1){
            secondInpt.disabled = true
        }

        // Simple star icon, you can replace it with a font icon or image
        var starContainer = document.createElement('span');


        if (!allTestsQuestions[test_Id]) {
            allTestsQuestions[test_Id] = {}; // Initialize the test_Id key if it doesn't exist
        }

        if (!allTestsQuestions[test_Id]['starQuestions']) {
            allTestsQuestions[test_Id]['starQuestions'] = []; // Initialize starQuestions as an empty array
        }

        var paper_data = ques['paperdata'][paper_id]
        
        if (paper_data){
            // console.log('paper_data',paper_data)
            if(paper_data['starQuestion'] == 'Y'){                                                    
                starContainer.innerHTML = `<i class="fas fa-star customStarCursor" data-star="Y" id="starQuestion_Q_${ques['questionId']}_${subTopicId}_testId_${test_Id}" onclick="markAsStarQuestion(${ques['questionId']},${subTopicId},${test_Id})"></i>`;  
                allTestsQuestions[test_Id]['starQuestions'].push({"qid":  ques['questionId'], 'star_flag': 'Y'})
            }
            else{                                                                               
                starContainer.innerHTML = `<i class="far fa-star customStarCursor" data-star="N" id="starQuestion_Q_${ques['questionId']}_${subTopicId}_testId_${test_Id}" onclick="markAsStarQuestion(${ques['questionId']},${subTopicId},${test_Id})"></i>`;
                allTestsQuestions[test_Id]['starQuestions'].push({"qid":  ques['questionId'], 'star_flag': 'N'})  
            }
        } else {
            
            if(ques['starQuestion'] == 'Y'){                                                    
                starContainer.innerHTML = `<i class="fas fa-star customStarCursor" data-star="Y" id="starQuestion_Q_${ques['questionId']}_${subTopicId}_testId_${test_Id}" onclick="markAsStarQuestion(${ques['questionId']},${subTopicId},${test_Id})"></i>`;  
                allTestsQuestions[test_Id]['starQuestions'].push({"qid":  ques['questionId'], 'star_flag': 'Y'})
            }
            else{                                                                               
                starContainer.innerHTML = `<i class="far fa-star customStarCursor" data-star="N" id="starQuestion_Q_${ques['questionId']}_${subTopicId}_testId_${test_Id}" onclick="markAsStarQuestion(${ques['questionId']},${subTopicId},${test_Id})"></i>`;
                allTestsQuestions[test_Id]['starQuestions'].push({"qid":  ques['questionId'], 'star_flag': 'N'})  
            }
        }

        var questionCheckBox = document.createElement('div')
        questionCheckBox.classList.add('questionElements')
        questionCheckBox.append(firstInpt, secondInpt, starContainer)

        if (paper_data){

            if(paper_data['paperQuestion'] == 'Y'){
                
                if(paper_data?.staticOrDynamic){
                    if(paper_data['staticOrDynamic'] == 'S'){
                        questionHasToBeSelected.push(firstInpt.id)
                    }

                    if(paper_data['staticOrDynamic'] == 'D'){
                        questionHasToBeSelected.push(secondInpt.id)
                    }

                }

            }
        }

        if(PaperType_ == 'S'){
            if(ques['questionType'] == 'M' || ques['questionType'] == 'B' || ques['questionType'] == 'P' || ques['questionType'] == 'A' || ques['questionType'] == 'V'){
                questionContainer.append(questionElement ,questionCheckBox);
                questionsContainer.append(questionContainer);
            }
        }
        else if(PaperType_ == 'E'){
            if(ques['questionType'] == 'C' || ques['questionType'] == 'R'){
                questionContainer.append(questionElement ,questionCheckBox);
                questionsContainer.append(questionContainer);
            }
        }
        else if(PaperType_ == 'I'){
            if(ques['questionType'] == 'I'){

                // hide dynamic questions count input container
                dynamicInputLabelContainer.hidden = true
                
                // star question was not in the interview
                starContainer.hidden = true

                // hide the dynamic check box
                secondInpt.hidden = true

                questionContainer.append(questionElement ,questionCheckBox);
                questionsContainer.append(questionContainer);
            }
        }

        // checking for show more questions flag
        var showMoreLabelCOntainer
        if (ques?.moreQuestions) {
            if(ques['moreQuestions'] == 'Y'){
                var showMoreMainContainer = document.createElement('div');
                showMoreMainContainer.classList.add('showMoreMainContainer');
                showMoreMainContainer.innerHTML = `<span class="showMoreText" onclick="showMoreQuestions( ${skill_Id}, ${topicId}, ${subTopicId},${test_Id},'${PaperType_}')">Show more Questions</span>`;

                showMoreLabelCOntainer = showMoreMainContainer;
            }
        }
        
    }

    var complexitySepraters = document.createElement('div')
    complexitySepraters.classList.add('containersSepratersCustomCls')
    
    if(showMoreLabelCOntainer == undefined){
        showMoreLabelCOntainer = ''
    }

    complexityMainContainer.append(questionsContainer ,showMoreLabelCOntainer ,complexitySepraters);

    //  return the main container
    return complexityMainContainer;

}


function questionCheckAsSelected(){

    // console.log('questionHasToBeSelected',questionHasToBeSelected)
    for (let quesId = 0; quesId < questionHasToBeSelected.length; quesId++) {

        let element = questionHasToBeSelected[quesId];

        if(element){

            var elementHasChecked = document.getElementById(element)

            if(elementHasChecked){
                // console.log('***',elementHasChecked)

                elementHasChecked.checked = true;
    
                if(elementHasChecked.checked){

                    var elementData = elementHasChecked.dataset

                    if(elementData){

                        var ElementTestId = elementData['testid']
                        var ElementSubtopicId = elementData['subtopic']
                        var ElementType = elementData['type']
                        var ElementQid = elementData['qid']
                        var ElementComplexity = elementData['complexity']
    
                        if(!allTestsQuestions[ElementTestId]){
                            allTestsQuestions[ElementTestId] = {};
                        }

                        if(!allTestsQuestions[ElementTestId]['staticQuestions']){
                            allTestsQuestions[ElementTestId]['staticQuestions'] = [];
                        }
                        
                        // orginial
                        if (!allTestsQuestions[ElementTestId][ElementSubtopicId]) {
                            allTestsQuestions[ElementTestId][ElementSubtopicId] = {
                                veryLow:  { qIds: [] },
                                low:      { qIds: [] },
                                medium:   { qIds: [] },
                                high:     { qIds: [] },
                                veryHigh: { qIds: [] }
                            };
                        }
    
                        if(ElementComplexity == 'verylow'){
                            ElementComplexity = 'veryLow'
                        }
    
                        if(ElementComplexity == 'veryhigh'){
                            ElementComplexity = 'veryHigh'
                        }

                        // console.log('>>>>>',ElementQid);
                        

                        if(ElementQid){
    
                            // checking questions are static questions are dynamic question
                            // static questions
                            if(ElementType == 'S'){
                                // Push the question ID to the appropriate ElementQid array
                                allTestsQuestions[ElementTestId]['staticQuestions'].push(parseInt(ElementQid))
                            }
                            
                            if(ElementType == 'D'){
                                // Push the question ID to the appropriate ElementQid array
                                allTestsQuestions[ElementTestId][ElementSubtopicId][ElementComplexity]['qIds'].push(parseInt(ElementQid));
                            }
        
                            if(ElementType == 'screening'){
                                // Push the question ID to the appropriate ElementQid array
                                allTestsQuestions[ElementTestId]['staticQuestions'].push(parseInt(ElementQid))
                            }
    
                        }
    
                    }
                    else{
                        console.log('Question data was not in the element');
                    }
                }
    
            }

        }

    }
    
    questionHasToBeSelected = []

}


// make a normal question to star question , when every user click on the icon we change the dataset of the icon
// question id , subtopic id, test id
function markAsStarQuestion(question_id , subtopic_id, test_id){
    
    if(subtopic_id){
        // starQuestion_Q_131_11_testId_202
        var starQuestionId = `starQuestion_Q_${question_id}_${subtopic_id}_testId_${test_id}`

        var CheckBoxElement = document.getElementById(`questionId_${question_id}_${test_id}_S`)

        // console.log('CheckBoxElement',CheckBoxElement);
        
        if(CheckBoxElement){
            if(CheckBoxElement.checked){

                var starElement = document.getElementById(starQuestionId)
                if(starElement){

                    var starData = starElement.dataset
                    
                    if(starData['star'] == 'N'){
                        starData['star'] = 'Y'
                        starElement.className = ''
                        starElement.classList.add('fas','fa-star','customStarCursor')

                        updateStarVariableStatus(question_id,test_id,starData['star'])
                    }
                    else{
                        starData['star'] = 'N'
                        starElement.className = ''
                        starElement.classList.add('far','fa-star','customStarCursor')
                        updateStarVariableStatus(question_id,test_id,starData['star'])
                    }

                    // console.log('starData',starData['star']);
                    

                }
                else{
                    console.log('can not found the star element');
                }
                



            }
            else{
                console.log('element was not checked');
            }
        }
        else{
            console.log('can not find question checked element');
        }

    }
    else{
        var starQuestionId = `starQuestion_Q_${question_id}_subTopic_BasicScreening_testId_${test_id}`
        
        var CheckBoxElement = document.getElementById(`questionId-${test_id}_${question_id}`)

        if(CheckBoxElement){
            if(CheckBoxElement.checked){

                var starElement = document.getElementById(starQuestionId)
                if(starElement){

                    var starData = starElement.dataset
                    
                    if(starData['star'] == 'N'){
                        starData['star'] = 'Y'
                        starElement.className = ''
                        starElement.classList.add('fas','fa-star','customStarCursor')

                        updateStarVariableStatus(question_id,test_id,starData['star'])
                    }
                    else{
                        starData['star'] = 'N'
                        starElement.className = ''
                        starElement.classList.add('far','fa-star','customStarCursor')

                        updateStarVariableStatus(question_id,test_id,starData['star'])
                    }

                }
                else{
                    console.log('can not found the star element');
                }

            }
            else{
                console.log('element was not checked');
            }
        }
        else{
            console.log('can not find question checked element');
        }
        
    }

}


// it get's ten more questions
// and append to the same container
function showMoreQuestions( skillId, topic_Id ,subTopicId, TestCardId, paper_Type){
    var complexityQuestionsContainer = document.getElementById(`complexitySubTopicQuestions_${subTopicId}_testId_${TestCardId}`)
    var complexityQuestionsDataSet = complexityQuestionsContainer.dataset
    var complexity = complexityQuestionsDataSet['complexitytype']

    if(complexity){

        // get the last question id
        var FndlastQuestionId = complexityQuestionsContainer.querySelector('ol').lastElementChild.id
        var elementLenght = FndlastQuestionId.split('_')
        var questId = FndlastQuestionId.split('_')[elementLenght.length - 1]

        if(questId){

            // adding loading style to the container
            complexityQuestionsContainer.style.cursor = 'wait'

            // hide the show more container
            var showMoreContainer = complexityQuestionsContainer.querySelector('.showMoreMainContainer')
            showMoreContainer.hidden = true

            const getQuestions = {
                subTopicId: subTopicId,
                complexityType: complexity,
                lastQuestionId: questId,
                paperType : paper_Type,
                paperid : testsList[TestCardId]['paperid']

            };
        
            // Prepare data to be sent to the backend
            var final_data = {
                "data": JSON.stringify(getQuestions),
                csrfmiddlewaretoken: CSRF_TOKEN,
            };

            console.log('card-data',allTestsQuestions[TestCardId]);
            
        
            try {

                $.post(CONFIG['acert'] + "/api/show-more-questions", final_data, function(res) {
                
                    if (res.statusCode == 0) {
                        if (res.data) {
                            // Call the function after the data is received
                            genrateComplexityQuestionsWithHtml(skillId, topic_Id, subTopicId, res.data, TestCardId);
                        }
                        complexityQuestionsContainer.style.cursor = 'default';
                    }

                }).fail(function(error) {
                    console.error("Error occurred during API call:", error);
                });
                
            } 
            catch (error) {
                console.error('Failed to send data to backend:', error);
            }

        }
        else{
            console.log("can't find the last question id when click on the show more questions");
        }

    }
    else{
        console.log('complexity Not Found');
    }

}



function genrateComplexityQuestionsWithHtml(skillId, topic_Id, subTopicId, questionsLst, TestCardId){

    var newQuesLst = questionsLst['newQuestionsLst']
    var complexityContainer = document.getElementById(`complexitySubTopicQuestions_${subTopicId}_testId_${TestCardId}`)
    var findOlElement = complexityContainer.querySelector('ol')
    var showMoreLabelContainer = complexityContainer.querySelector('.showMoreMainContainer')
    showMoreLabelContainer.hidden = false

    for (let question_ = 0; question_ < newQuesLst.length; question_++) {
        
        let ques = newQuesLst[question_];
        var questionContainer = document.createElement('div');
        questionContainer.classList.add('customQuestionContainer')
        questionContainer.id = `QuestionContainerId_${ques['questionId']}`

        var questionElement = document.createElement('li');
        questionElement.id = `question_id_${ques['questionId']}`
        // questionElement.innerText = ques['question'].replace(/\\u[0-9A-Fa-f]{4}/g, '').replace(/\s+/g, ' ');  // Assuming ques is an object with 'question' key
        questionElement.innerText = ques['question']
        
        let questionMarks = ques['marks']
        console.log('questionMarks',ques)
        let complex = null

        if(ques['questionComplexity'] == 1){
            complex = 'verylow'
        }
        if(ques['questionComplexity'] == 2){
            complex = 'low'
        }
        if(ques['questionComplexity'] == 3){
            complex = 'medium'
        }
        if(ques['questionComplexity'] == 4){
            complex = 'heigh'
        }
        if(ques['questionComplexity'] == 5){ 
            complex = 'veryheigh'
        }

        let firstInpt = document.createElement('input');
        firstInpt.type = 'checkbox';  // Assuming you want checkboxes
        firstInpt.classList.add('form-check-input','mx-4')
        firstInpt.id = `questionId_${ques['questionId']}_${TestCardId}_S`
        firstInpt.dataset['qid'] = ques['questionId']
        firstInpt.dataset['testid'] = TestCardId
        firstInpt.dataset['skill'] = skillId
        firstInpt.dataset['topic'] = topic_Id
        firstInpt.dataset['subtopic'] = subTopicId
        firstInpt.dataset['marks'] = questionMarks
        firstInpt.dataset['complexity'] = complex
        firstInpt.dataset['type'] = 'S'
        firstInpt.setAttribute(
            'onclick',
            `addQuestionsToList(${ques['questionId']}, this.id,${TestCardId})`
        );

        // Another checkbox
        let secondInpt = document.createElement('input');
        secondInpt.type = 'checkbox'; 
        secondInpt.classList.add('form-check-input','mx-4','dynamic-custom-checkbox')
        secondInpt.id = `questionId_${ques['questionId']}_${TestCardId}_D`
        secondInpt.dataset['qid'] = ques['questionId']
        secondInpt.dataset['testid'] = TestCardId
        secondInpt.dataset['skill'] = skillId
        secondInpt.dataset['topic'] = topic_Id
        secondInpt.dataset['subtopic'] = subTopicId
        secondInpt.dataset['marks'] = questionMarks
        secondInpt.dataset['complexity'] = complex
        secondInpt.dataset['type'] = 'D'
        secondInpt.setAttribute(
            'onclick',
            `addQuestionsToList(${ques['questionId']}, this.id,${TestCardId})`
        );


        if(ques['paperQuestion'] == 'Y'){
            
            if(ques?.staticOrDynamic){
                if(ques['staticOrDynamic'] == 'S'){
                    questionHasToBeSelected.push(firstInpt.id)
                }

                if(ques['staticOrDynamic'] == 'D'){
                    questionHasToBeSelected.push(secondInpt.id)
                }

            }

        }

        // Simple star icon, you can replace it with a font icon or image
        var starContainer = document.createElement('span');
        // starContainer.innerHTML = '<i class="fas fa-star"></i>';

        if(ques['starQuestion'] == 'Y'){                                                    // question id , subtopic id, test id
            starContainer.innerHTML = `<i class="fas fa-star customStarCursor" data-star="Y" id="starQuestion_Q_${ques['questionId']}_${subTopicId}_testId_${TestCardId}" onclick="markAsStarQuestion(${ques['questionId']},${subTopicId},${TestCardId})"></i>`;  
            allTestsQuestions[TestCardId]['starQuestions'].push({"qid":  ques['questionId'], 'star_flag': 'Y'})
        }
        else{                                                                               // question id , subtopic id, test id
            starContainer.innerHTML = `<i class="far fa-star customStarCursor" data-star="N" id="starQuestion_Q_${ques['questionId']}_${subTopicId}_testId_${TestCardId}" onclick="markAsStarQuestion(${ques['questionId']},${subTopicId},${TestCardId})"></i>`;  
            allTestsQuestions[TestCardId]['starQuestions'].push({"qid":  ques['questionId'], 'star_flag': 'Y'})
        }

        var questionCheckBox = document.createElement('div')
        questionCheckBox.classList.add('questionElements')
        questionCheckBox.append(firstInpt, secondInpt, starContainer)

        questionContainer.append(questionElement ,questionCheckBox);

        findOlElement.append(questionContainer)

        // checking for show more questions flag
        if (ques?.moreQuestions) {
            if(ques['moreQuestions'] == 'N'){
                showMoreLabelContainer.hidden = true 
            }
        }

        questionCheckAsSelected();

    }

}


// basic screening questions genrate add to html (JD Based Generated Questions)
async function genrateHtmlWithScreeningBasicQuestion(testId) {
    
    try {
        const screeningBasicQuestionsList = await getAllBasicScreeningQuestions(testId);
        // console.log('--------------')
        // console.log('testId',testId)
        // console.log('screeningBasicQuestionsList',screeningBasicQuestionsList)
        // console.log('--------------')
        var basicQuestionsContainer = document.getElementById(`basicScreeningContainer_${testId}`)
            
        var olElement = document.createElement('ol')
        basicQuestionsContainer.append(olElement)

        // Proceed with generating HTML after data is fetched
        for (let question_ = 0; question_ < screeningBasicQuestionsList.length; question_++) {

            let ques = screeningBasicQuestionsList[question_];

            // console.log('ques',ques)
            var questionContainer = document.createElement('div');
            questionContainer.classList.add('customQuestionContainer');
            questionContainer.id = `QuestionContainerId_${ques['questionId']}`;

            var questionElement = document.createElement('li');
            questionElement.id = `question_id_${ques['questionId']}`;
            // questionElement.innerText = ques['question'].replace(/\\u[0-9A-Fa-f]{4}/g, '').replace(/\s+/g, ' ');
            questionElement.innerText = ques['question']
            questionMarks = ques['marks']

            var firstInpt = document.createElement('input');
            firstInpt.type = 'checkbox';
            firstInpt.classList.add('form-check-input', 'mx-2');
            firstInpt.id = `questionId-${testId}_${ques['questionId']}`
            firstInpt.dataset['qid'] = ques['questionId']
            firstInpt.dataset['type'] = 'screening'
            firstInpt.dataset['testid'] = testId
            firstInpt.dataset['marks'] = ques['questionMarks']
            firstInpt.setAttribute(
                'onclick',
                `addQuestionsToList(${ques['questionId']},this.id,${testId})`
            );

            // console.log('quesid',ques['questionId'])

            
            if (!allTestsQuestions[testId]) {
                allTestsQuestions[testId] = {}; // Initialize the testId key if it doesn't exist
            }
    
           

            if(!allTestsQuestions[testId]['staticQuestions']){
                allTestsQuestions[testId] = {'staticQuestions':[]};
            }

            // if (!allTestsQuestions[testId]['starQuestions']) {
            //     allTestsQuestions[testId]['starQuestions'] = []; // Initialize starQuestions as an empty array
            //     console.log('Star questions initialized for testId:', testId, allTestsQuestions[testId]);
            // }

            if (!allTestsQuestions[testId]['starQuestions']) {
                allTestsQuestions[testId]['starQuestions'] = []; // Initialize starQuestions as an empty array
            }

            if (ques['paperQuestion'] == 'Y'){
                firstInpt.checked = true;

                if(!allTestsQuestions[testId]['staticQuestions']){
                    allTestsQuestions[testId] = {'staticQuestions':[]};
                }

                allTestsQuestions[testId]['staticQuestions'].push(parseInt(ques['questionId']))

            }

            var starContainer = document.createElement('span');
            
            // console.log('allTestsQuestions[testId]',allTestsQuestions[testId])
            // console.log('Star Question',allTestsQuestions[testId]['starQuestions'])

            if(ques['starQuestion'] == 'Y'){                                                // question id , subtopic id, test id
                starContainer.innerHTML = `<i class="fas fa-star customStarCursor" data-star="Y" id="starQuestion_Q_${ques['questionId']}_subTopic_BasicScreening_testId_${testId}" onclick="markAsStarQuestion(${ques['questionId']},null,${testId})"></i>`; 
                allTestsQuestions[testId]['starQuestions'].push({"qid":  ques['questionId'], 'star_flag': 'Y'})
            }
            else{                                                                           // question id , subtopic id, test id
                starContainer.innerHTML = `<i class="far fa-star customStarCursor" data-star="N" id="starQuestion_Q_${ques['questionId']}_subTopic_BasicScreening_testId_${testId}" onclick="markAsStarQuestion(${ques['questionId']},null,${testId})"></i>`;  
                allTestsQuestions[testId]['starQuestions'].push({"qid":  ques['questionId'], 'star_flag': 'N'})
            }

            var questionCheckBox = document.createElement('div');
            questionCheckBox.classList.add('questionElements');
            questionCheckBox.append(firstInpt, starContainer);

            questionContainer.append(questionElement, questionCheckBox);

            olElement.append(questionContainer)
            
        }

    }
    catch (error) {
        console.error("Error fetching screening questions:", error);
    }
}


// Function to handle clicks on skills/topics/subtopics
function showskillOrTopicOrSubtopicOrQuestions(elementId) {
    unhideTheTopicContainer(elementId);
}


function unhideTheTopicContainer(elementId) {

    var clickedElement = document.getElementById(elementId);
    var clickedElementDataSet = clickedElement.dataset;

    if(clickedElementDataSet['data'] != 'N'){

        var testId = clickedElementDataSet['testid'];

        if (clickedElementDataSet['type'] == 'skill') {
            if (skillsClickesTracker[`previousSelectedSkill_${testId}`] != elementId) {

                // add css style to clicked skill
                clickedElement.classList.add('active-skill');
                
                // un hide the topic main container
                // finding the topic container which is realted to a specific skill
                var skillTopicContainerId = `SkillTopicContainer_${clickedElementDataSet['skillid']}_Test_${testId}`;
                // finding the topic container
                var topicContainerElement = document.getElementById(skillTopicContainerId);
                // un hide the topic container
                topicContainerElement.hidden = false;

                // selecting the topic with active class
                var skillTopicsListContainer = topicContainerElement.querySelector('.skillsListTopicsList')

                // check for if there any active topic in the skill
                var topicFirstElement
                if(skillTopicsListContainer.querySelector('.active-skill')){
                    // finding the active topic from the topic container
                    topicFirstElement = skillTopicsListContainer.querySelector('.active-skill')
                }
                // if there is no active topic selected in the topics from a skill we will directily active first element 
                else{
                    topicFirstElement = topicContainerElement.querySelector('.skillsListTopicsList').firstElementChild;
                    if(topicFirstElement){
                    topicFirstElement.classList.add('active-skill');
                    }
                }

                // extracting the data from a topic element for unhide the subtopic container.
                var topicDataSet
                if(topicFirstElement){
                    topicDataSet = topicFirstElement.dataset;
                }

                if(topicDataSet){

                    // subtopic container id bulid with topic data with dataset.
                    var skillSubTopicContainerId = `SkillSubTopicContainer_${topicDataSet['topicid']}_Skill_${topicDataSet['skillid']}_Test_${testId}`;

                    // finding the subtopic container
                    var subTopicContainerElement = document.getElementById(skillSubTopicContainerId);

                    // un hide the topic container
                    subTopicContainerElement.hidden = false;

                    var skillSubTopicsListContainer = subTopicContainerElement.querySelector('.skillsList')

                    // checking for active subtopic
                    var subtopicFirstElement
                    if(skillSubTopicsListContainer.querySelector('.active-skill')){
                        subtopicFirstElement = skillSubTopicsListContainer.querySelector('.active-skill');
                    }
                    // if there no active subtopic we select the first one as active skill
                    else{
                        subtopicFirstElement = subTopicContainerElement.querySelector('.skillsList').firstElementChild;
                        subtopicFirstElement.classList.add('active-skill');
                    }

                    // Hidding and removing styles
                    // removing css skill from skill make as normal skill
                    var previousSkillElement = document.getElementById(skillsClickesTracker[`previousSelectedSkill_${testId}`]);
                    if (previousSkillElement) {
                        previousSkillElement.classList.remove('active-skill');
                        previousSkillElement.classList.add('inactive-skill');
                    }

                    // hidding the Topic container
                    var previousTopicContainer = document.getElementById(skillsClickesTracker[`previousSelectedTopicContainerId_${testId}`]);
                    if (previousTopicContainer) {
                        previousTopicContainer.hidden = true;
                    }

                    // hidding the SubTopic container
                    var previousSubTopicContainer = document.getElementById(skillsClickesTracker[`previousSelectedSubTopicContainerId_${testId}`]);
                    if (previousSubTopicContainer) {
                        previousSubTopicContainer.hidden = true;
                    }

                    // hidding the SubTopic Questions container
                    var previousSubTopicQuestionsContainer = document.getElementById(skillsClickesTracker[`previousSelectedSubTopicQuestionsContainerId_${testId}`]);
                    if (previousSubTopicQuestionsContainer) {
                        previousSubTopicQuestionsContainer.hidden = true;
                    }

                    // un hide the SubTopic Questions container
                    let clickedSubtopicElementkey = subtopicFirstElement.dataset['subtopicid']
                    let SubTopicQuestionsContainer = document.getElementById(`SubTopicQuestionsContainer_${clickedSubtopicElementkey}_test_${testId}`)
                    if(SubTopicQuestionsContainer){
                        SubTopicQuestionsContainer.hidden = false
                    }
                    else{
                        console.warn('trying to find the subtopic questions but there is no question in this subtopic');
                    }

                    skillsClickesTracker[`previousSelectedSkill_${testId}`] = elementId;
                    skillsClickesTracker[`previousSelectedTopicId_${testId}`] = topicFirstElement.id;
                    skillsClickesTracker[`previousSelectedTopicContainerId_${testId}`] = topicContainerElement.id;
                    skillsClickesTracker[`previousSelectedSubTopicId_${testId}`] = subtopicFirstElement.id;
                    skillsClickesTracker[`previousSelectedSubTopicContainerId_${testId}`] = subTopicContainerElement.id;
                    skillsClickesTracker[`previousSelectedSubTopicQuestionsContainerId_${testId}`] = `SubTopicQuestionsContainer_${clickedSubtopicElementkey}_test_${testId}`
                }
                else{
                    
                    // hide the topic container 
                    var topicContainerHid = document.getElementById(`SkillTopicContainer_${clickedElementDataSet['skillid']}_Test_${testId}`)
                    if(topicContainerHid){
                        topicContainerHid.hidden = true
                        console.log('Skill does not have topic data, sub topic data container is hide');
                    }
                    
                }

                
            }
        } 
        else if (clickedElementDataSet['type'] == 'topic') {

            if (skillsClickesTracker[`previousSelectedTopicId_${testId}`] != elementId) {
                var clickedTopicElement = document.getElementById(elementId);
                var clickedTopicDataSet = clickedTopicElement.dataset;

                // removing the pervious selected topic css active class remove
                var previousTopicElement = document.getElementById(skillsClickesTracker[`previousSelectedTopicId_${testId}`]);
                if (previousTopicElement) {
                    previousTopicElement.classList.remove('active-skill');
                }

                // hidding the SubTopic Container
                var previousSubTopicContainer = document.getElementById(skillsClickesTracker[`previousSelectedSubTopicContainerId_${testId}`]);
                if (previousSubTopicContainer) {
                    previousSubTopicContainer.hidden = true;
                }

                // hide the subtopic Questions Container
                var previousSubTopicContainer = document.getElementById(skillsClickesTracker[`previousSelectedSubTopicContainerId_${testId}`]);
                if (previousSubTopicContainer) {
                    previousSubTopicContainer.hidden = true;
                }

                // hidding the SubTopic Questions container
                var previousSubTopicQuestionsContainer = document.getElementById(skillsClickesTracker[`previousSelectedSubTopicQuestionsContainerId_${testId}`]);
                if (previousSubTopicQuestionsContainer) {
                    previousSubTopicQuestionsContainer.hidden = true;
                }

                // add active css class to new clicked topic element
                clickedTopicElement.classList.add('active-skill');

                // un hide the subTopic container with topic extracted data.
                var subTopicContainerId = `SkillSubTopicContainer_${clickedTopicDataSet['topicid']}_Skill_${clickedTopicDataSet['skillid']}_Test_${testId}`;
                var subTopicContainerElement = document.getElementById(subTopicContainerId);
                subTopicContainerElement.hidden = false;

                // finding the subtopics list container
                var skillSubTopicsListContainer = subTopicContainerElement.querySelector('.skillsList')
                
                // finding the active subtopic from the subtopic container.
                var subtopicFirstElement
                if(skillSubTopicsListContainer.querySelector('.active-skill')){
                    subtopicFirstElement = skillSubTopicsListContainer.querySelector('.active-skill')
                }
                // if we can not find the active subtopic we select the first subtopic from the topic
                else{
                    subtopicFirstElement = subTopicContainerElement.querySelector('.skillsList').firstElementChild;
                    subtopicFirstElement.classList.add('active-skill');
                }

                // hidding the SubTopic Questions container
                var previousSubTopicQuestionsContainer = document.getElementById(skillsClickesTracker[`previousSelectedSubTopicQuestionsContainerId_${testId}`]);
                if (previousSubTopicQuestionsContainer) {
                    previousSubTopicQuestionsContainer.hidden = true;
                }

                // un hide the SubTopic Questions container
                let clickedSubtopicElementkey = subtopicFirstElement.dataset['subtopicid']
                let SubTopicQuestionsContainer = document.getElementById(`SubTopicQuestionsContainer_${clickedSubtopicElementkey}_test_${testId}`)
                if(SubTopicQuestionsContainer){
                    SubTopicQuestionsContainer.hidden = false
                }
                else{
                    console.warn('trying to find the subtopic questions but there is no question in this subtopic');
                }
                
                skillsClickesTracker[`previousSelectedTopicId_${testId}`] = elementId;
                skillsClickesTracker[`previousSelectedSubTopicId_${testId}`] = subtopicFirstElement.id;
                skillsClickesTracker[`previousSelectedSubTopicContainerId_${testId}`] = subTopicContainerElement.id;
                skillsClickesTracker[`previousSelectedSubTopicQuestionsContainerId_${testId}`] = `SubTopicQuestionsContainer_${clickedSubtopicElementkey}_test_${testId}`
            }
        }
        else if (clickedElementDataSet['type'] == 'subtopic') {

            if (skillsClickesTracker[`previousSelectedSubTopicId_${testId}`] != elementId) {

                var previousSubTopicElement = document.getElementById(skillsClickesTracker[`previousSelectedSubTopicId_${testId}`]);
                if (previousSubTopicElement) {

                    // remove active css from the pervious 
                    previousSubTopicElement.classList.remove('active-skill');

                    // add active css styles to clicked element
                    var clickedSubTopicElement = document.getElementById(elementId);
                    clickedSubTopicElement.classList.add('active-skill')

                    // makeing the selected subtopic as pervious subtopic
                    skillsClickesTracker[`previousSelectedSubTopicId_${testId}`] = clickedSubTopicElement.id;

                    // un hide the SubTopic Questions container
                    let clickedSubtopicElementkey = clickedSubTopicElement.dataset['subtopicid']
                    let SubTopicQuestionsContainer = document.getElementById(`SubTopicQuestionsContainer_${clickedSubtopicElementkey}_test_${testId}`)
                    if(SubTopicQuestionsContainer){
                        SubTopicQuestionsContainer.hidden = false
                    }
                    else{
                        console.warn('trying to find the subtopic questions but there is no question in this subtopic');
                    }

                    // hidding the SubTopic Questions container
                    var previousSubTopicQuestionsContainer = document.getElementById(skillsClickesTracker[`previousSelectedSubTopicQuestionsContainerId_${testId}`]);
                    if (previousSubTopicQuestionsContainer) {
                        previousSubTopicQuestionsContainer.hidden = true;
                    }

                    skillsClickesTracker[`previousSelectedSubTopicQuestionsContainerId_${testId}`] = `SubTopicQuestionsContainer_${clickedSubtopicElementkey}_test_${testId}`

                }

            }

        }

    }
    
}


// Perfect
// function addPerfectScrollbarToDynamicElement(testId) {
//     var skillsListScroll = document.getElementById(`skillListScroll_${testId}`);
//     if (skillsListScroll) {
//         new PerfectScrollbar(skillsListScroll, {
//             wheelPropagation: false,
//             suppressScrollY: true
//         });
//     }
// }


function activeScreeningTab(element){
    
    if(element){
        let elementId = element.id
        let TestCardId = elementId.split('_')[elementId.split('_').length - 1]

        var screnningfirstTab = document.getElementById(`screeningTab_1_${TestCardId}`)
        var screnningSecondTab = document.getElementById(`screeningTab_2_${TestCardId}`)
        var dynamicQuestionsContainerToHide = document.getElementById(`dynamicQuestionsContainer_${TestCardId}`)

        if(element.classList.contains('active-screeningTab')){
            // clicking on a active tab nothing to do here
        }
        else{
            var basicQuestionsContainer = document.getElementById(`basicScreeningContainer_${TestCardId}`)
            
            if(element.dataset['screeningtype'] == 'basic'){

                screnningfirstTab.classList.add('active-screeningTab')
                screnningSecondTab.classList.remove('active-screeningTab')
                // un hide the basic questions container
                
                basicQuestionsContainer.hidden = false
                // KnowledgeQuestionsContainer.hidden = true

                // hide the dynamic questions count
                if(dynamicQuestionsContainerToHide){
                    dynamicQuestionsContainerToHide.hidden = true
                }
                else{
                    console.log(" can't hide the dynamic questions container ");
                }

                // hide the skills & topics & subtopics Container
                let skillsAndTopicsAndSubTopicsContainerId = `skillsAndTopicsAndSubtopicsContainer_${TestCardId}`
                let skillsTopicSubtopicsElement = document.getElementById(skillsAndTopicsAndSubTopicsContainerId)
                if(skillsTopicSubtopicsElement){
                    skillsTopicSubtopicsElement.hidden = true
                }
                else{
                    console.log('try to show basic screening test question by hidding the knowledge test questions container but somthing went wrong');
                }
                
                $('#knowledge_'+TestCardId).hide();
                $('#screening_basic_'+TestCardId).show();
                
            }

            if(element.dataset['screeningtype'] == 'knowledge'){

                // add active class to screening tab
                screnningSecondTab.classList.add('active-screeningTab')
                // remove active class to screening tab
                screnningfirstTab.classList.remove('active-screeningTab')
                
                // hidde the JD questions container
                basicQuestionsContainer.hidden = true

                // un hide the dynamic questions count
                if(dynamicQuestionsContainerToHide){
                    dynamicQuestionsContainerToHide.hidden = false
                }
                else{
                    console.log(" can't un hide the dynamic questions container ");
                }

                // un hidding the skills & topics & subtopics Container
                let skillsAndTopicsAndSubTopicsContainerId = `skillsAndTopicsAndSubtopicsContainer_${TestCardId}`
                let skillsTopicSubtopicsElement = document.getElementById(skillsAndTopicsAndSubTopicsContainerId)
                if(skillsTopicSubtopicsElement){
                    skillsTopicSubtopicsElement.hidden = false
                }
                else{
                    console.log('try to show knowledge test screening question by hidding the basic test questions container but somthing went wrong');
                }

                $('#knowledge_'+TestCardId).show();
                $('#screening_basic_'+TestCardId).hide();
                // click first skill if there is no active skill.
                // clickOnFirstSkill(TestCardId)
            }

        }
        //  Clear search when switching tabs
        const testId = element.id.split('_').pop();
        const searchInput = document.querySelector(
            `.jd-search-input[data-testid="${testId}"]`
        );

        if (searchInput) {
            searchInput.value = "";
            searchJDQuestions(searchInput);
        }

    }
    else{
        console.log('Screening Swatch tab does not have test card Id');
    }
}


//  when we click on new screen or coding or interview button this function will be called 
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


// this function Update the Test data and Save's the Test Data.
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

                    console.log("data ::::",data);

                    // test is updated and update card data
                    if ('updateEvent' in data && data['updateEvent'] == 'Y'){

                        var key_ = data['id']
                        testsList[[key_]] =  data
                        updateCardAfterSaveData(testsList,data['id'])

                        // call the test questions main container 

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
                        // creating new test card
                        // test is add and create card
                        var key_ = data[0]['id'] // test card id
                        testsList[[key_]] =  data[0]
                        testsList_.push(key_)

                        // creating keys with values null for the Test skills click tracker
                        skillsClickesTracker[`previousSelectedSkill_${key_}`] = null;
                        skillsClickesTracker[`previousSelectedTopicId_${key_}`] = null;
                        skillsClickesTracker[`previousSelectedTopicContainerId_${key_}`] = null;
                        skillsClickesTracker[`previousSelectedSubTopicId_${key_}`] = null;
                        skillsClickesTracker[`previousSelectedSubTopicContainerId_${key_}`] = null;
                        skillsClickesTracker[`previousSelectedSubTopicQuestionsContainerId_${key_}`] = null

                        testType = testType

                        // it create test cards and appends to webpage.
                        addTestCardToShow(testName,promotValue,testType,data[0])

                        // when loading the page initalTestCard was guides to show which test when it is opening
                        initalTestCard = false
                        PaperTitle = data[0]['papertitle']
                        let paperType__ = data[0]['papertype']

                        // this function create the questions containenr for the newly created test 
                        TestCardQuestionsMainContainers(key_, paperType__,PaperTitle , 'show', initalTestCard)

                        // this function call when a new test created, with out page referesh 
                        // this function create skills and topics and subtopics with html and show in webapge.
                        skillsListShowInHtml(key_, skillsTopicSubtopics, paperType__, null);

                        // clicking on the newlly created test card
                        document.getElementById(paperType__+'_'+data[0]['id']).click();

                    }

                }
            }

        })

    }

}


//  this function update the Html TEST card on webpage after save the data
function updateCardAfterSaveData(allTestsList,testId){
    
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

// this function create Test card and put that test card in Test cards Main Container
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
    highlightTestButton(testType);

}


// when we click on the Test card this function will be called , and add Styles and Hide and Unhide the Test's Questions Container.
function selectTest(element_id){

    console.log('element_id::::::::::',element_id);
    

    if (element_id != perviousSelectedTest){

        var test_type = element_id.split('_')[0]
        var workFlowId = element_id.split('_')[1]

        if(element_id){

            var workFlowId = element_id.split('_')[1]
            var currentSelectedTestWorkFlow = document.getElementById('TestContainer_'+workFlowId)
            if(currentSelectedTestWorkFlow){
                currentSelectedTestWorkFlow.hidden = false
            }

        }

        if(perviousSelectedTest){

            var perviousSelectedTestId = perviousSelectedTest.split('_')[1]
            var perviousSelectedTestWorkFlow = document.getElementById('TestContainer_'+perviousSelectedTestId)
            if(perviousSelectedTestWorkFlow){
                perviousSelectedTestWorkFlow.hidden = true
            }

        }

        // it only allow get library one and create html container 
        if (!instialSelectTest.includes(workFlowId)) {
            instialSelectTest.push(workFlowId)
            // getPapersLibraries(test_type, workFlowId);
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
        testBox.classList.remove('unActiveTestCard')
        testBox.classList.add(custumStyles)

        if (perviousSelectedTest){
            var testBox = document.getElementById(perviousSelectedTest)
            if(testBox){
                testBox.classList.remove('activeTestCars-screen-test', 'activeTestCars-coding-test', 'activeTestCars-interview-test')
                testBox.classList.add('unActiveTestCard')
            }
        }

        if(test_type == "S"){

            let element1 = document.getElementById("screeningTab_1_"+workFlowId);
            let element2 = document.getElementById("screeningTab_2_"+workFlowId);

            if (element1 && element1.classList.contains("active-screeningTab")) {
                $('#knowledge_'+workFlowId).hide();
                $('#screening_basic_'+workFlowId).show();

                $('#new_question_type').val('B').change();

            } else if (element2 && element2.classList.contains("active-screeningTab")) {
                $('#knowledge_'+workFlowId).show();
                $('#screening_basic_'+workFlowId).hide();
                $('#new_question_type').val('B').change();
            }

        }else {
            $('#knowledge_'+workFlowId).show();
            $('#screening_basic_'+workFlowId).hide();
        }

        
    }
    
    perviousSelectedTest = element_id
    // document.getElementById('TestCardQuestionsContainersList').hidden = false

}


function clickOnFirstSkill(testId){

    // checking for the active skill if test does not have any active skill we click directly first skill first topic and first subtopic.
    if(skillsClickesTracker[`previousSelectedSkill_${testId}`] == null){
        
        let skillsAndTopicsAndSubtopicsContainerId = `skillsAndTopicsAndSubtopicsContainer_${testId}`
        let skillsAndTopicsAndSubTopicsContainerElement = document.getElementById(skillsAndTopicsAndSubtopicsContainerId)
        
        let skillsListOfElements = skillsAndTopicsAndSubTopicsContainerElement.querySelector('.skillsList')
        var allSkillsList = skillsListOfElements.querySelectorAll('.skill')

        for (let checkSkill = 0; checkSkill < allSkillsList.length; checkSkill++) {
            const element = allSkillsList[checkSkill];
            if(element.dataset['data'] == 'Y'){
                element.click(); 
                break
            }
        }
    
    }

}


// when we click Test card Update Icon Button this function will be called.
function updateTest(event, currentSelectedtestId) {
    testCreateOrUpdate = 'update';
    cureentTestId = currentSelectedtestId;
    event.stopPropagation();
    openUpdateTestModel(currentSelectedtestId);
}


//  this function open Test model with releated data.
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


// this function allow to copy the integration script for carrer page integration
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


// when we click on the delete Icon on a test card Delete Model opens for Conformation.
function deleteTestModalOpen(testid) {

    var testTilt =  document.getElementById('testTitle_'+testid).innerText
    document.getElementById('delectCancelBtn').hidden = false
    document.getElementById('deleteTestConformation').hidden = false
    document.getElementById('conformationForDelete').innerText =  'Are sure want to delete '+testTilt
    document.getElementById('deleteTestConformation').dataset['deletetestid'] = testid
    $('#modalToggle').modal('show')
    event.stopPropagation();
    // TestWithLibrariesAndQuestions
    
}


// This function executes when we conformed the Delete test. 
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
                var removeQuestionsContainer = document.getElementById(`TestContainer_${testCardDetails['testData']['id']}`)

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


// Save Interviewers List 
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


// this function executes when user Click on the Publish Button or Stop Button.
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
                    // $('#publishValidationModal').modal('show')
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

// enable Or Disable the Hold percentage in the Test card.
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


// it changes the Status in html
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


// when we click Publish Button this function will be called
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


// career page Modal Open integrations script button
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


// document.addEventListener('DOMContentLoaded', () => {
//     const loader = document.getElementById('candidates-loader');

//     window.addEventListener('load', () => {
//         loader.style.display = 'none';
//     });
// });


// don't remove here to ==============================================
// {
//     "202": { // test will be there in the position of 202
//       "staticQuestions": [],
//       "11": { // subtopic id will be there in the position of 11
//             "veryLow": {
//                 "qCount": 0,
//                 "qIds": [1]
//             },
//             "low": {
//                 "qCount": 0,
//                 "qIds": []
//             },
//             "medium": {
//                 "qCount": 0,
//                 "qIds": []
//             },
//             "high": {
//                 "qCount": 0,
//                 "qIds": []
//             },
//             "veryHigh": {
//                 "qCount": 0,
//                 "qIds": []
//             }
//       }
//     }
// }
// here ===============================================================
  

function addQuestionsToList(Qid, elementId, test_Id) {


    var elements = document.querySelectorAll(`#${elementId}`);
    
    if (elements.length === 0) {
        console.error('No elements found with the provided ID.');
        return;
    }

    var targetElement = Array.from(elements).find(el => el.dataset.testid == test_Id);

    if (targetElement) {

        var questionElement_ = targetElement;

        var questionDataSet = questionElement_.dataset;

        // Extract attributes
        let testCardId    = questionDataSet['testid']; 
        let questionType_ = questionDataSet['type']; 
        let subTopic_Id   = questionDataSet['subtopic']; 
        let complexType   = questionDataSet['complexity']?.toLowerCase(); 
        let QueMarks      = questionDataSet['marks']

        // Normalize complexType keys
        const complexityMapping = {
            verylow: 'veryLow',
            low: 'low',
            medium: 'medium',
            high: 'high',
            veryhigh: 'veryHigh'
        };
        complexType = complexityMapping[complexType] || complexType;

        // check if the test card is persent
    
        if(!allTestsQuestions[testCardId]){
            allTestsQuestions[testCardId] = {};
        }
        
        if(!allTestsQuestions[testCardId]['staticQuestions']){
            allTestsQuestions[testCardId]['staticQuestions'] = [];
        }

        // orginial
        // // Check if the subTopic is present
        if(subTopic_Id) {

            if (!allTestsQuestions[testCardId][subTopic_Id]) {
                allTestsQuestions[testCardId][subTopic_Id] = {
                    veryLow: { qIds: [] },
                    low: { qIds: [] },
                    medium: { qIds: [] },
                    high: { qIds: [] },
                    veryHigh: { qIds: [] }
                };
            }
        }

        // Check if the subTopic is present
        // if (!allTestsQuestions[testCardId][subTopic_Id]) {
        //     allTestsQuestions[testCardId][subTopic_Id] = {
        //         veryLow: { qCount: 0, qIds: [] },
        //         low: { qCount: 0, qIds: [] },
        //         medium: { qCount: 0, qIds: [] },
        //         high: { qCount: 0, qIds: [] },
        //         veryHigh: { qCount: 0, qIds: [] }
        //     };
        // }

        // checking questions are static questions are dynamic question
        // static questions adding in to static questions list
        if(questionType_ == 'S'){

            if(questionElement_.checked){
                // Push the question ID to the appropriate qIds array
                allTestsQuestions[testCardId]['staticQuestions'].push(Qid)

                if(testsList[testCardId]['papertype'] == 'S'){

                    // increase the test static questions count
                    // screening static questions count in to html
                    var screeningStaticQuesElementId = `screeningStaticQuestionsCount_${testCardId}`
                    var lstOfCountElements = document.getElementsByClassName(screeningStaticQuesElementId)
        
                    for (let elem_ = 0; elem_ < lstOfCountElements.length; elem_++) {
                        let element = lstOfCountElements[elem_];
        
                        if(element.innerText){
                            let totalCount_ = parseInt(element.innerText) + 1
                            element.innerText = totalCount_
                        }
                    }
        
                    // increase the paper weightage 
                    // paper weightage
                    var screeningWeightAgeElementId = `screeningTestId_${testCardId}`
                    var lstOfElements = document.getElementsByClassName(screeningWeightAgeElementId)
        
                    for (let elem = 0; elem < lstOfElements.length; elem++) {
                        let element = lstOfElements[elem];
        
                        if(element.innerText){
                            let totalMarks_ = parseInt(element.innerText) + parseInt(QueMarks)
                            element.innerText = totalMarks_
                        }
        
                    }

                }

                if(testsList[testCardId]['papertype'] == 'E'){

                    var WeightAgeElementId = `TestWeightage_${testCardId}`
                    var element_ = document.getElementById(WeightAgeElementId)

                    if(element_) {
                        if(element_.innerText){
                            let totalMarks_ = parseInt(element_.innerText) + parseInt(QueMarks)
                            element_.innerText = totalMarks_
                        }
                    }

                    var StaticQuesElementId = `StaticQuestionsCount_${testCardId}`
                    var Qcount_Element = document.getElementById(StaticQuesElementId)

                    if(Qcount_Element) {

                        if(Qcount_Element.innerText){
                            let totalCount_ = parseInt(Qcount_Element.innerText) + 1
                            Qcount_Element.innerText = totalCount_
                        }
                    }

                }

                if(testsList[testCardId]['papertype'] == 'I'){

                    let interviewTestQuesId = document.getElementById(`InterviewQuestionsCount_${testCardId}`)
                    if(interviewTestQuesId){
                        if(interviewTestQuesId.innerText){
                            let interQuestotalCount_ = parseInt(interviewTestQuesId.innerText) + 1
                            interviewTestQuesId.innerText = interQuestotalCount_
                        }
                    }

                }


            }
            else{

                // Push the question ID to the appropriate qIds array
                let checkQuestionInLst = allTestsQuestions[testCardId]['staticQuestions'].includes(Qid)
                if(checkQuestionInLst){
                    let index = allTestsQuestions[testCardId]['staticQuestions'].indexOf(Qid);
                    
                    // if index not equal to minus one that means index value is found 
                    if (index !== -1) {
                        // remove from the list
                        allTestsQuestions[testCardId]['staticQuestions'].splice(index, 1);
                    }
                }

                if(testsList[testCardId]['papertype'] == 'S'){

                    // Decrease the test static questions count
                    var screeningStaticQuesElementId = `screeningStaticQuestionsCount_${testCardId}`
                    var lstOfCountElements = document.getElementsByClassName(screeningStaticQuesElementId)

                    for (let elem_ = 0; elem_ < lstOfCountElements.length; elem_++) {
                        let element = lstOfCountElements[elem_];
                        // element.innerText = papersData[workflowData['paperid']]['staticQuestionsCount']

                        if(element.innerText){
                            let totalCount_ = parseInt(element.innerText) - 1
                            element.innerText = totalCount_
                        }
                    }

                    // decerease the paper weightage 
                    // paper weightage
                    var screeningWeightAgeElementId = `screeningTestId_${testCardId}`
                    var lstOfElements = document.getElementsByClassName(screeningWeightAgeElementId)

                    for (let elem = 0; elem < lstOfElements.length; elem++) {
                        let element = lstOfElements[elem];

                        if(element.innerText){
                            let totalMarks_ = parseInt(element.innerText) - parseInt(QueMarks)
                            element.innerText = totalMarks_
                        }

                    }

                }

                if(testsList[testCardId]['papertype'] == 'E'){

                    // test total score
                    var WeightAgeElementId = `TestWeightage_${testCardId}`
                    var element_ = document.getElementById(WeightAgeElementId)

                    if(element_) {
                        if(element_.innerText){
                            let totalMarks_ = parseInt(element_.innerText) - parseInt(QueMarks)
                            element_.innerText = totalMarks_
                        }

                    }

                    // questions count
                    var StaticQuesElementId = `StaticQuestionsCount_${testCardId}`
                    var Qcount_Element = document.getElementById(StaticQuesElementId)

                    if(Qcount_Element) {
                        if(Qcount_Element.innerText){
                            let totalCount_ = parseInt(Qcount_Element.innerText) - 1
                            Qcount_Element.innerText = totalCount_
                        }
                    }

                }

                if(testsList[testCardId]['papertype'] == 'I'){

                    let interviewTestQuesId = document.getElementById(`InterviewQuestionsCount_${testCardId}`)
                    if(interviewTestQuesId){
                        if(interviewTestQuesId.innerText){
                            let interQuestotalCount_ = parseInt(interviewTestQuesId.innerText) - 1
                            interviewTestQuesId.innerText = interQuestotalCount_
                        }
                    }

                }

            }

        }

        // checking questions are static questions are dynamic question
        // dynamic questions adding in to questions list
        if(questionType_ == 'D'){

            if(questionElement_.checked){
                // Push the question ID to the appropriate qIds array
                allTestsQuestions[testCardId][subTopic_Id][complexType].qIds.push(Qid);
            }
            else{
                
                let checkQuestionInLst = allTestsQuestions[testCardId][subTopic_Id][complexType].qIds.includes(Qid)
                if(checkQuestionInLst){
                    let index = allTestsQuestions[testCardId][subTopic_Id][complexType].qIds.indexOf(Qid);
                    
                    if (index !== -1) {
                        // remove from the list
                        allTestsQuestions[testCardId][subTopic_Id][complexType].qIds.splice(index, 1);
                    }
                }

            }

        }

        // checking questions are static questions are dynamic question
        // jd basic screening questions in to the static questions list
        if(questionType_ == 'screening'){

            if(questionElement_.checked){
                // Push the question ID to the appropriate qIds array
                allTestsQuestions[testCardId]['staticQuestions'].push(Qid)

                // increase the test static questions count
                // screening static questions count in to html
                var screeningStaticQuesElementId = `screeningStaticQuestionsCount_${testCardId}`
                var lstOfCountElements = document.getElementsByClassName(screeningStaticQuesElementId)

                for (let elem_ = 0; elem_ < lstOfCountElements.length; elem_++) {
                    let element = lstOfCountElements[elem_];

                    if(element.innerText){
                        let totalCount_ = parseInt(element.innerText) + 1
                        element.innerText = totalCount_
                    }
                }

                // increase the paper weightage 
                // paper weightage
                var screeningWeightAgeElementId = `screeningTestId_${testCardId}`
                var lstOfElements = document.getElementsByClassName(screeningWeightAgeElementId)

                for (let elem = 0; elem < lstOfElements.length; elem++) {
                    let element = lstOfElements[elem];

                    if(element.innerText){
                        let totalMarks_ = parseInt(element.innerText) + parseInt(QueMarks)
                        element.innerText = totalMarks_
                    }

                }

            }
            else{
                
                // Push the question ID to the appropriate qIds array
                let checkQuestionInLst = allTestsQuestions[testCardId]['staticQuestions'].includes(Qid)
                if(checkQuestionInLst){
                    let index = allTestsQuestions[testCardId]['staticQuestions'].indexOf(Qid);
                    
                    // if index not equal to minus one that means index value is found 
                    if (index !== -1) {
                        // remove from the list
                        allTestsQuestions[testCardId]['staticQuestions'].splice(index, 1);
                    }
                }

                // Decrease the test static questions count
                var screeningStaticQuesElementId = `screeningStaticQuestionsCount_${testCardId}`
                var lstOfCountElements = document.getElementsByClassName(screeningStaticQuesElementId)

                for (let elem_ = 0; elem_ < lstOfCountElements.length; elem_++) {
                    let element = lstOfCountElements[elem_];
                    // element.innerText = papersData[workflowData['paperid']]['staticQuestionsCount']

                    if(element.innerText){
                        let totalCount_ = parseInt(element.innerText) - 1
                        element.innerText = totalCount_
                    }
                }

                // decerease the paper weightage 
                // paper weightage
                var screeningWeightAgeElementId = `screeningTestId_${testCardId}`
                var lstOfElements = document.getElementsByClassName(screeningWeightAgeElementId)

                for (let elem = 0; elem < lstOfElements.length; elem++) {
                    let element = lstOfElements[elem];

                    if(element.innerText){
                        let totalMarks_ = parseInt(element.innerText) - parseInt(QueMarks)
                        element.innerText = totalMarks_
                    }

                }
                

            }

        }
       
    } else {
        console.log('No element found with the matching test-id');
    }

    

}


function savePaper(BtnElement) {
    return new Promise((resolve, reject) => {

        var saveBtnElementDataset = document.getElementById(BtnElement).dataset
        let testid_ = saveBtnElementDataset['testid']

        // console.log('testid_',testid_)

        let paperType = testsList[testid_]['papertype']
        var testTitle = document.getElementById(`testTitle_${testid_}`)

        var testid = Number(testid_);

        // console.log('allTestsQuestions',allTestsQuestions)

        dataObj = {
            'paperid'              :  testsList[testid_]['paperid'],
            'paperType'            :  paperType,
            'paperTitle'           :  testTitle.innerText,
            'questionsData'        :  allTestsQuestions[testid]
        };

        
        checkCandidateRegistration().then(data => {

            if(data == 'N'){

                var final_data = {
                    "data": JSON.stringify(dataObj),
                    csrfmiddlewaretoken: CSRF_TOKEN,
                };
        
                // First AJAX call
                $.post(CONFIG['acert'] + "/api/save-paper", final_data, function (res) {
        
                    if (res.statusCode == 0 && res.data) {
        
                        var data = res.data;
                        selectedPaper = data;
        
                        var dataObj = {
                            'createOrUpdate' : 'update',
                            'createdPaperid': data['createdPaperid'],
                            'testId': testid,
                            'jdId': jdId
                        };
        
                        var final_data_jd = {
                            'data': JSON.stringify(dataObj),
                            csrfmiddlewaretoken: CSRF_TOKEN,
                        };
        
                        // Saving Paper id in hireline with this api
                        $.post(CONFIG['portal'] + "/api/jd-add-or-update-test", final_data_jd, function (res) {
                            resolve(data); // Resolve the promise with the data after both calls
                            showSuccessMessage('Saved Successfully');
                        }).fail((error) => {
                            reject(error); // Reject on second API call error
                        });
        
                    } 
                    else {
                        reject(new Error("Failed to create paper")); // Reject on first API call error
                    }
                }).fail((error) => {
                    console.error('Error in first API call:', error);
                    reject(error); // Reject on first API call error
                });

            }


        })
        .catch(err => {
            console.error("Error occurred:", err);
        });

    })
}


// user entered an number in the input or changed the input value is updated in the varibale
function dynamicQuestionscountSave(inputElement){

    var dynamicInptElement = document.getElementById(inputElement)
    var dynInptDataSet = dynamicInptElement.dataset

    var testId = dynInptDataSet['testid']
    var subTopic_Id = dynInptDataSet['subtopicid']

    if(subTopic_Id){

        var complexitytype = dynInptDataSet['complexitytype']
        
        if (!allTestsQuestions[testId]) {
            allTestsQuestions[testId] = {'staticQuestions':[]};
        }

        // Check if the subTopic is present
        if (!allTestsQuestions[testId][subTopic_Id]) {
            allTestsQuestions[testId][subTopic_Id] = {
                veryLow: { qCount: 0, qIds: [] },
                low: { qCount: 0, qIds: [] },
                medium: { qCount: 0, qIds: [] },
                high: { qCount: 0, qIds: [] },
                veryHigh: { qCount: 0, qIds: [] }
            };
        }

        allTestsQuestions[testId][subTopic_Id][complexitytype]['qCount'] = dynamicInptElement.value

        updateTestWeightage(allTestsQuestions[testId],testId)
        

    }
    
    if(testsList[testId]['papertype'] == 'S'){

        let codingDynamicElemId = `DynamicQuestionsCount_${testId}`
        let codingDynamicElem = document.getElementById(codingDynamicElemId)

        // if(codingDynamicElem){
        //     var labelCount = parseInt(codingDynamicElem.innerText)
 
        //     if(isNaN(labelCount)){
        //         labelCount = 0
        //     }

        //     var labelValue = labelCount - parseInt(dynamicQuestionCountInputValueBackup)

        //     var DynInptVal = parseInt(dynamicInptElement.value)

        //     if(isNaN(parseInt(dynamicInptElement.value))){
        //         DynInptVal = 0
        //     }
            
        //     let finalDynCount = labelValue + DynInptVal

        //     codingDynamicElem.innerText = finalDynCount
            
        //     if(isNaN(dynamicInptElement.value)){
        //         dynamicQuestionCountInputValueBackup = 0
        //     }
        //     else{
        //         dynamicQuestionCountInputValueBackup = parseInt(dynamicInptElement.value)
        //     }

        //     console.log('dynamicQuestionCountInputValueBackup',dynamicQuestionCountInputValueBackup)

        // }
        let totalDynamicCount = 0;
    let dynamicInputs = document.querySelectorAll(
        `input[data-testid='${testId}'].dynamicInpt`
    );

    dynamicInputs.forEach((inp) => {
        let val = parseInt(inp.value);
        if (!isNaN(val)) totalDynamicCount += val;
    });

    // Update the total label
    let totalLabelElem = document.getElementById(`DynamicQuestionsCount_${testId}`);
    if (totalLabelElem) {
        totalLabelElem.innerText = totalDynamicCount;
    }

    // Backup new value
    dynamicQuestionCountInputValueBackup = newValue;

    console.log(`Updated total for Test ${testId}: ${totalDynamicCount}`);
        

    }

    if(testsList[testId]['papertype'] == 'E'){

        let codingDynamicElemId = `DynamicQuestionsCount_${testId}`
        let codingDynamicElem = document.getElementById(codingDynamicElemId)

        // if(codingDynamicElem){
        //     var labelCount = parseInt(codingDynamicElem.innerText)
 
        //     if(isNaN(labelCount)){
        //         labelCount = 0
        //     }

        //     var labelValue = parseInt(dynamicQuestionCountInputValueBackup) - labelCount

        //     var DynInptVal = dynamicInptElement.value
        //     if(parseInt(dynamicInptElement.value) == NaN){
        //         DynInptVal = 0
        //     }

            
        //     let finalDynCount = labelValue + parseInt(DynInptVal)

        //     if (isNaN(finalDynCount)) {
        //         console.log('Found NaN');
        //         codingDynamicElem.innerText = dynamicQuestionCountInputValueBackup - labelCount
        //     }
        //     else{
        //         codingDynamicElem.innerText = labelValue + parseInt(DynInptVal)
        //     }

            
        //     if(isNaN(dynamicInptElement.value)){
        //         dynamicQuestionCountInputValueBackup = 0
        //     }
        //     else{
        //         dynamicQuestionCountInputValueBackup = parseInt(dynamicInptElement.value)
        //     }

        // }
        let totalDynamicCount = 0;
    let dynamicInputs = document.querySelectorAll(
        `input[data-testid='${testId}'].dynamicInpt`
    );

    dynamicInputs.forEach((inp) => {
        let val = parseInt(inp.value);
        if (!isNaN(val)) totalDynamicCount += val;
    });

    // Update the total label
    let totalLabelElem = document.getElementById(`DynamicQuestionsCount_${testId}`);
    if (totalLabelElem) {
        totalLabelElem.innerText = totalDynamicCount;
    }

    // Backup new value
    dynamicQuestionCountInputValueBackup = newValue;

    console.log(`Updated total for Test ${testId}: ${totalDynamicCount}`);
       

        console.log('dynamicQuestionCountInputValueBackup',dynamicQuestionCountInputValueBackup)

    }

}


function DynamicInputValueBackUp(element_Id){

    dynamicQuestionCountInputValueBackup = 0

    var Elem_ = document.getElementById(element_Id)
    if(Elem_){
        if(Elem_.value){
            dynamicQuestionCountInputValueBackup = Elem_.value
        }
        else{
            dynamicQuestionCountInputValueBackup = 0
        }
    }

    console.log('dynamicQuestionCountInputValueBackup',dynamicQuestionCountInputValueBackup)

}


// this function takes data from the backend and insert in to a variable that contains static and dynamic question that variable go to backend
function fillDynamicQuestionsInputField(TestCardid_,data) {

    for (const subtopicId in data) {
        const complexities = data[subtopicId];

        if(!allTestsQuestions[TestCardid_]){
            allTestsQuestions[TestCardid_] = {};
        }

        if(!allTestsQuestions[TestCardid_]['staticQuestions']){
            allTestsQuestions[TestCardid_]['staticQuestions'] = [];
        }
        
        if (!allTestsQuestions[TestCardid_][subtopicId]) {
            allTestsQuestions[TestCardid_][subtopicId] = {
                veryLow:  { qCount: 0 ,  qIds: [] },
                low:      { qCount: 0 ,  qIds: [] },
                medium:   { qCount: 0 ,  qIds: [] },
                high:     { qCount: 0 ,  qIds: [] },
                veryHigh: { qCount: 0 ,  qIds: [] }
            };
        }
        
        // inserting dynamic questions count in to the variable.
        if(subtopicId){

            if(complexities){
                allTestsQuestions[TestCardid_][subtopicId]['veryLow']['qCount'] = parseInt(complexities['veryLow'])
                allTestsQuestions[TestCardid_][subtopicId]['low']['qCount'] = parseInt(complexities['low'])
                allTestsQuestions[TestCardid_][subtopicId]['medium']['qCount'] = parseInt(complexities['medium'])
                allTestsQuestions[TestCardid_][subtopicId]['high']['qCount'] = parseInt(complexities['high'])
                allTestsQuestions[TestCardid_][subtopicId]['veryHigh']['qCount'] = parseInt(complexities['veryHigh'])
            }

        }


        for (const complexity in complexities) {

            // Construct the dynamic element ID
            const elementId = `DynamicInput_TestId_${TestCardid_}_subTopic_${subtopicId}_complex_${complexity}`;
            
            // Get the input element by ID
            const complexityInputElement = document.getElementById(elementId);

            // If the element exists, set its value
            if (complexityInputElement) {
                complexityInputElement.value = complexities[complexity];
            } 
        }
    }

}


// check candidate's before save paper

function checkCandidateRegistration() {
    return new Promise((resolve, reject) => {
        const dataObjs = { 'jd_id': jdId };

        const final_data = {
            'data': JSON.stringify(dataObjs),
            csrfmiddlewaretoken: CSRF_TOKEN,
        };

        $.post(CONFIG['portal'] + "/api/check-jd-candidate-registration", final_data)
            .done(function (res) {
                res.data = "N"
                if (res.statusCode === 0) {

                    if (res.data === "Y") {
                        Swal.fire({
                            icon: 'info',
                            title: 'The candidate is already registered for this Job Description and cannot be edited.',
                            confirmButtonText: 'OK',
                            confirmButtonColor: '#274699',
                        });
                    }

                    // Resolve with the API data
                    resolve(res.data);
                } else {
                    console.error('Error: Unexpected statusCode in response');
                    reject('Unexpected statusCode');
                }
            })
            .fail(function () {
                console.error('Error in checking the candidate registration (API call failed)');
                // reject('API call failed');
            });
    });
}
//  code in between

function paperQuestionsCountAndMarksSetInHTML(papersData){
    
    for (var key in workFlowDetails) {
                    
        if (workFlowDetails.hasOwnProperty(key)) {

            var workflowData = workFlowDetails[key]
            var testCardId__ = workflowData['id']

            if(papersData[workflowData['paperid']]){

                if(workflowData['papertype'] == 'S'){

                    // paper weightage
                    var screeningWeightAgeElementId = `screeningTestId_${testCardId__}`
                    var lstOfElements = document.getElementsByClassName(screeningWeightAgeElementId)

                    for (let elem = 0; elem < lstOfElements.length; elem++) {
                        let element = lstOfElements[elem];
                        element.innerText = papersData[workflowData['paperid']]['totalMarks']
                    }

                    // screening static questions count in to html
                    var screeningStaticQuesElementId = `screeningStaticQuestionsCount_${testCardId__}`
                    var lstOfCountElements = document.getElementsByClassName(screeningStaticQuesElementId)

                    for (let elem_ = 0; elem_ < lstOfCountElements.length; elem_++) {
                        let element = lstOfCountElements[elem_];
                        element.innerText = papersData[workflowData['paperid']]['staticQuestionsCount']
                    }

                    // inserting dynamic questions count in to html
                    var ScrenningDynamicQuesCountElement = document.getElementById(`DynamicQuestionsCount_${testCardId__}`)

                    if(ScrenningDynamicQuesCountElement){
                        ScrenningDynamicQuesCountElement.innerText = papersData[workflowData['paperid']]['dynamicQuestionsCount']
                    }

                    // papersData[workflowData['paperid']]['totalMarks']

                }

                if(workflowData['papertype'] == 'E'){

                    papersData[workflowData['paperid']]['totalMarks']

                    var codingPaperTotalWeightage = document.getElementById(`TestWeightage_${testCardId__}`)
                    if(codingPaperTotalWeightage){
                        codingPaperTotalWeightage.innerText = papersData[workflowData['paperid']]['totalMarks']
                    }

                    var codingStaticQues = document.getElementById(`StaticQuestionsCount_${testCardId__}`)
                    if(codingStaticQues){
                        codingStaticQues.innerText = papersData[workflowData['paperid']]['staticQuestionsCount']
                    }

                    var codingDynamicQuesCount = document.getElementById(`DynamicQuestionsCount_${testCardId__}`)
                    if(codingDynamicQuesCount){
                        codingDynamicQuesCount.innerText = papersData[workflowData['paperid']]['dynamicQuestionsCount']
                    }

                }

                if(workflowData['papertype'] == 'I'){

                    var interviewQuestionsCount = document.getElementById(`InterviewQuestionsCount_${testCardId__}`)
                    if(interviewQuestionsCount){
                        interviewQuestionsCount.innerText = papersData[workflowData['paperid']]['staticQuestionsCount']
                    }
                    
                }

            }

        }
    }
}


function updateStarVariableStatus(question_id, testId, starFlag) {

    // Check if the test ID exists and starQuestions array is available
    if (allTestsQuestions[testId] && Array.isArray(allTestsQuestions[testId]['starQuestions'])) {

        // Find the question by `qid` and update its star_flag
        let question = allTestsQuestions[testId]['starQuestions'].find(q => q.qid === question_id);

        if (question) {
            question.star_flag = starFlag;  // Update star_flag if question exists
            console.log('Question updated successfully:', question);
        } else {
            console.warn(`Question with ID ${question_id} not found. Adding new entry.`);
            allTestsQuestions[testId]['starQuestions'].push({ "qid": question_id, "star_flag": starFlag });
        }

    } else {
        console.error(`Test ID "${testId}" not found or starQuestions is not an array.`);
    }

    console.log('Updated allTestsQuestions:', allTestsQuestions);
}


function updateTestWeightage(test_data, test_id) {
    // console.log('test_data', test_data);
    // console.log('test_id', test_id);

    const subtopicKeys = Object.keys(test_data).filter(key => key !== "starQuestions" && key !== "staticQuestions");

    const weightageCategories = ["veryLow", "low", "medium", "high", "veryHigh"];

    let totalMarks = 0; // Consolidated total for all test IDs

    // Calculate total marks for dynamic questions
    subtopicKeys.forEach(subtopicId => {
        weightageCategories.forEach(category => {
            if (test_data[subtopicId][category] && test_data[subtopicId][category].qIds.length > 0) {
                // Get the first qId from the category
                const firstQId = test_data[subtopicId][category].qIds[0];

                // Construct the element ID dynamically using the first qId
                const elementId = `questionId_${firstQId}_${test_id}_D`;
                const element = document.getElementById(elementId);

                if (element) {
                    const marks = parseFloat(element.getAttribute('data-marks')) || 0;

                    // Multiply qCount by the marks and add to total
                    totalMarks += test_data[subtopicId][category].qCount * marks;
                }
            }
        });
    });

    console.log("Consolidated Total Marks from Dynamic Questions:", totalMarks);

    // Calculate total marks for static questions
    if (test_data.staticQuestions && Array.isArray(test_data.staticQuestions)) {
        test_data.staticQuestions.forEach(qId => {
            
            let element = document.getElementById(`questionId_${qId}_${test_id}_S`);
        
            // If not found, try to find the element without the "_S" suffix (JD Based Questions)
            if (!element) {
                element = document.getElementById(`questionId-${test_id}_${qId}`);
            }

            if (element) {
                const marks = parseFloat(element.getAttribute('data-marks')) || 0;
                totalMarks += marks; // Add the marks for the static question
            }
            else{
                console.log('Element not found');
                
            }
        });
    }

    console.log("Consolidated Total Marks (including Static Questions):", totalMarks);
   

    // Assuming the total marks are to be updated in the corresponding <span> element
    const totalMarksElement = document.querySelector(`#TestWeightage_${test_id}`);

    if (totalMarksElement) {
        totalMarksElement.textContent = totalMarks; // Update the span with the total marks
    } else {
        console.log(`No element found for TestWeightage_${test_id}`);
    }
}




function createNewQuestionContainer(test_id, paperType){

    if(paperType == 'I'){
       styleElement =  `style = "margin-top:1rem"`
    }else {
        styleElement = ''
    }

    var create_question_container = `
        <div class="jd_create_question_div"  id="screening_basic_${test_id}"> 
            <button class="btn btn-primary" ${styleElement} onclick="createQuestionModel(${test_id},'${paperType}','screening')"><i class="fas fa-plus"></i> &nbsp; Add question</button>
        </div>
        <div class="jd_create_question_div" id="knowledge_${test_id}" style="display:none"> 
            <button class="btn btn-primary" ${styleElement} onclick="createQuestionModel(${test_id},'${paperType}','knowledge')"><i class="fas fa-plus"></i> &nbsp; Add question</button>
        </div>
        `

    return create_question_container

}


function createQuestionModel(test_id, paperType, QuesType) {

    // addKnowledgeBasedQuestion(255,{
    //     'question_id': 3080, 
    //     'question_text': 'Knowledge Question 1',
    //     'question_type': 'B',
    //     'question_complexity': '2',
    //     'star_question': 'N', 
    //     'question_subject': 35, 
    //     'question_topic': 81, 
    //     'question_subtopic': 94, 
    //     'question_marks': '1'
    // },"S")

    if (QuesType == 'screening'){

        let subTopicElement = document.getElementById("new_question_subtopic_name");
        subTopicElement.textContent = "JD Screening";
        subTopicElement.setAttribute("data-new-question-typefor", 'basic-screening');
        subTopicElement.setAttribute("data-new-question-subtopicid", '');
        subTopicElement.setAttribute("data-test-id", test_id);
        subTopicElement.setAttribute("data-paper-type", paperType);
       
        $('#question-complexity-div').hide();
        $('#expected_response_div').show();

        let modalElement = document.getElementById('createQuestionModal');
        modalElement.removeAttribute("aria-hidden");

        var myModal = new bootstrap.Modal(modalElement);
        myModal.show();

    }else{

        let key = `previousSelectedSubTopicId_${test_id}`;
    
        let previousSelectedSubTopicId = skillsClickesTracker.hasOwnProperty(key) ? skillsClickesTracker[key] : null;
    
        let subTopicElement = document.getElementById("new_question_subtopic_name");
    
        if (previousSelectedSubTopicId) {
            let subTopicSourceElement = document.getElementById(previousSelectedSubTopicId);
            if (subTopicSourceElement) {
    
                let subTopicText = subTopicSourceElement.textContent.trim();
                let subTopicId = subTopicSourceElement.getAttribute("data-subtopicid");
                subTopicElement.textContent = subTopicText;
    
                subTopicElement.setAttribute("data-new-question-subtopicid", subTopicId);
                subTopicElement.setAttribute("data-test-id", test_id);
                subTopicElement.setAttribute("data-paper-type", paperType);
                subTopicElement.setAttribute("data-new-question-typefor", 'knowledge');
    
                if (paperType == "I"){
                    $('#expected_response_div').hide();
                    $('#new_question_type').val('I').change();
                    $('#question-complexity-div').show();
                }else {
                    $('#expected_response_div').show();
                    $('#new_question_type').val('B').change();
                    $('#question-complexity-div').show();
                }
    
                let modalElement = document.getElementById('createQuestionModal');
                modalElement.removeAttribute("aria-hidden");
    
                var myModal = new bootstrap.Modal(modalElement);
                myModal.show();
    
            } else {
                console.log("Element not found for ID:", subTopicId);
            }
        }
    }
}



document.getElementById('createQuestionModal').addEventListener('hidden.bs.modal', function () {
    let subTopicElement = document.getElementById("new_question_subtopic_name");
    
    if (subTopicElement) {
        subTopicElement.textContent = "N/A";

        subTopicElement.removeAttribute("data-create-question-subtopicid");

        $('#new_question_text').val('')
        $('#new_question_complexity').val(1)
        $('#save-new-question').prop('disabled', false);

    }
});


document.getElementById("save-new-question").onclick = function () {

    let subTopicElement = document.getElementById("new_question_subtopic_name");
    subtopic_id = subTopicElement.getAttribute("data-new-question-subtopicid");
    ques_typefor = subTopicElement.getAttribute("data-new-question-typefor");
    test_id = subTopicElement.getAttribute("data-test-id");
    paper_type = subTopicElement.getAttribute("data-paper-type");

    $('#new-question-form').unbind('submit').bind('submit', function (event) {
        event.preventDefault(); 
    })

    dataObjs = {
        'company_id': companyId,
        'subtopic_id': subtopic_id,
        'ques_typefor':ques_typefor,
        'question': $('#new_question_text').val(),
        'question_type': $('#new_question_type').val(),
        'question_complexity':$('#new_question_complexity').val(),
        'expected_answer':  $("input[name='expected-response']:checked").val(),
    }

    var final_data = {
        'data': JSON.stringify(dataObjs),
        csrfmiddlewaretoken: CSRF_TOKEN,
    }

    $('#save-new-question').prop('disabled', true);

    $.post(CONFIG['acert'] + "/api/hirelines-new-question", final_data, function (res) {
        if (res.statusCode == 0) {

            showSuccessMessage('New Question Added');

            $('#createQuestionModal').modal('hide');

            $('#save-new-question').prop('disabled', false);

            questionData = res.data

            if(ques_typefor == "basic-screening"){

                addNewBasicScreeningQuestion(test_id,questionData);

                scrollToSection(`QuestionContainerId_${questionData["question_id"]}`);

            }else {

                addKnowledgeBasedQuestion(test_id,questionData,paper_type);

                scrollToSection(`questionId_${questionData["question_id"]}_${test_id}_S`);

            }



        } else {

            showFailureMessage('Error in Adding new question. Please try again after some time');

        }
    }).fail(function () {
        showFailureMessage('Error in Adding new question. Please try again after some time');
        $('#save-new-question').prop('disabled', false);
    });

}


function addNewBasicScreeningQuestion(test_id,questionData){

    screeningContainer = document.getElementById(`basicScreeningContainer_${test_id}`);

    ol = screeningContainer.querySelector("ol");

    newQuestionElement = `
        <div class="customQuestionContainer" id="QuestionContainerId_${questionData["question_id"]}">
            <li id="question_id_${questionData["question_id"]}">${questionData["question_text"]}</li>
            <div class="questionElements">
                <input type="checkbox" class="form-check-input mx-2" id="questionId-${test_id}_${questionData["question_id"]}" data-qid="${questionData["question_id"]}" data-type="screening" data-testid="${test_id}" data-marks="${questionData["question_marks"]}" onclick="addQuestionsToList(${questionData["question_id"]},this.id,${test_id})">
                <span>
                    <i class="far fa-star customStarCursor" data-star="N" id="starQuestion_Q_${questionData["question_id"]}_subTopic_BasicScreening_testId_${test_id}" onclick="markAsStarQuestion(${questionData["question_id"]},null,${test_id})"></i>
                </span>
            </div>
        </div>
    `

    ol.insertAdjacentHTML("beforeend", newQuestionElement);

    const checkboxId = `questionId-${test_id}_${questionData["question_id"]}`;
    const checkbox = document.getElementById(checkboxId);

    if (checkbox) {
        checkbox.checked = true;
        addQuestionsToList(questionData["question_id"], checkboxId, test_id);
    }

    if (!allTestsQuestions[test_id]) {
        allTestsQuestions[test_id] = {}; // Initialize the test_id key if it doesn't exist
    }

    if (!allTestsQuestions[test_id]['starQuestions']) {
        allTestsQuestions[test_id]['starQuestions'] = []; // Initialize starQuestions as an empty array
    }

    allTestsQuestions[test_id]['starQuestions'].push({"qid":  questionData["question_id"], 'star_flag': 'N'}) 
    console.log("allTestsQuestions[test_id]",allTestsQuestions[test_id]);
    
}


function addKnowledgeBasedQuestion(test_id,questionData,paperType){

    let testQuestionsContainer = document.getElementById(`SubTopicQuestionsContainer_${questionData['question_subtopic']}_test_${test_id}`)

    if (!testQuestionsContainer) {
        testQuestionsContainer = document.createElement('div');
        testQuestionsContainer.id =
            `SubTopicQuestionsContainer_${questionData['question_subtopic']}_test_${test_id}`;
        testQuestionsContainer.hidden = false;

        const parent = document.getElementById(
            `SkillSubTopicContainer_${questionData['question_topic']}_Skill_${questionData['question_subject']}_Test_${test_id}`
        );

        if (parent) {
            parent.appendChild(testQuestionsContainer);
        } else {
            console.error('Subtopic parent container not found');
            return;
        }
    }

    let questionComplexity = questionData['question_complexity']

    let complexityMapping = {1:'verylow',2:'low',3:'medium',4:'high',5:'veryhigh'}

    let complexityType = complexityMapping[questionComplexity];

    let existingElement = testQuestionsContainer.querySelector(`[data-complexitytype="${complexityType}"]`);

    let generateQuestionData = [{
        'marks': questionData['question_marks'],
        'moreQuestions': "N",
        'paperQuestion': "N",
        'paperdata': {},
        'question': questionData['question_text'],
        'questionComplexity': questionData['question_complexity'],
        'questionId': questionData['question_id'],
        'questionType': questionData['question_type'],
        'skillId': questionData['question_subject'],
        'starQuestion': "N",
        'subTopicId': questionData['question_subtopic'],
        'topicId': questionData['question_topic'],
    }]

    let complexityContainer = createComplexityQuestionsContainer(
        generateQuestionData,
        questionData['question_subject'],
        questionData['question_topic'],
        questionData['question_subtopic'],
        test_id,
        paperType,
        complexityType,
        undefined
    )

    if(complexityContainer){

        if(existingElement){

            let existingQuestionsOl = existingElement.querySelector("ol");
    
            if (existingQuestionsOl) {
        
                let newOl = complexityContainer.querySelector("ol");
        
                if (newOl) {
    
                    let newDivs = newOl.querySelectorAll("div.customQuestionContainer");
                    console.log("newDivs",newDivs);
                    
                    newDivs.forEach(div => {
                        existingQuestionsOl.appendChild(div);
                    });

                    if(paperType != "I"){
                        setTimeout(() => updateDynamicContainerVisibility(existingElement,questionData['question_subtopic'],test_id), 0);
                    }


        
                } else {
                    console.log("Error: No <ol> found inside the generated complexity container.");
                }
    
            } else {
                console.log("Error: No <ol> found inside the existing complexity container.");
            }
    
        }else {
    
            let children = [...testQuestionsContainer.children];
            
            let inserted = false;
    
            for (let child of children) {
                let childComplexityType = child.getAttribute("data-complexitytype");
                let childComplexityIndex = Object.values(complexityMapping).indexOf(childComplexityType);
                let newComplexityIndex = Object.values(complexityMapping).indexOf(complexityType);
    
                if (newComplexityIndex < childComplexityIndex) {
                    testQuestionsContainer.insertBefore(complexityContainer, child);
                    inserted = true;
                    break;
                }
            }
    
            if (!inserted) {
                testQuestionsContainer.appendChild(complexityContainer);
            }

            if(paperType != "I"){
                setTimeout(() => updateDynamicContainerVisibility(complexityContainer,questionData['question_subtopic'],test_id), 0);
            }
        }

    }else {
        console.log("Error: Complexity container creation failed.");
    }

    setTimeout(() => {

        const staticCheckboxId = `questionId_${questionData['question_id']}_${test_id}_S`;
        const staticCheckbox = document.getElementById(staticCheckboxId);

        if (staticCheckbox && !staticCheckbox.checked) {
            staticCheckbox.checked = true;
            addQuestionsToList(
                questionData['question_id'],
                staticCheckboxId,
                test_id
            );
        }

    }, 0);
}


function scrollToSection(id) {
    document.getElementById(id).scrollIntoView({ behavior: "smooth" });
}

function updateDynamicContainerVisibility(complexityContainer,subTopicId,TestId) {
    let questionsOl = complexityContainer.querySelector("ol");
    
    if (questionsOl) {

        let dynamicContainer =  complexityContainer.querySelector(`#complexityDynamicContainer_subtopicId_${subTopicId}_testId_${TestId}`);
        
        let totalQuestions = questionsOl.querySelectorAll("div.customQuestionContainer").length;
        
        if (totalQuestions > 1 && dynamicContainer) {
            dynamicContainer.removeAttribute("hidden");

            let allInputs = questionsOl.querySelectorAll("div.customQuestionContainer input");
            allInputs.forEach(input => {
                input.removeAttribute("disabled");
            });
        }
    }
}










//  JS: Modal preview logic
function previewQuestions(testId, paperType) {
    // Show overlay modal (initially loading)
    document.getElementById("overlay").style.display = "flex";
    $("#preview_paper_title").html("Preview - " + (paperType === 'E' ? 'Coding' : paperType === 'I' ? 'Interview' : 'Screening'));
    $("#question_preview").html("<p>Loading preview questions...</p>");

    // Step 1: Fetch paper_id
    $.ajax({
        url: CONFIG["portal"] + `/api/get_paperid?test_id=${testId}`,
        type: "GET",
        success: function (res) {
            if (res.paper_id) {
                const paperId = res.paper_id;

                // Step 2: Fetch preview data
                $.ajax({
                    url: CONFIG["acert"] + "/api/preview",
                    type: "POST",
                    contentType: "application/json",
                    data: JSON.stringify({ paper_id: paperId }),

                    success: function (res2) {
                        if (res2.statusCode === 0 && res2.data) {
                            const questions = res2.data;
                            console.log("questions",questions)
                            $("#preview_paper_details").html(
                                `<span>Total Questions : ${questions.length} </span>`
                            );
                            $("#question_preview").html("");

                            questions.forEach((q, i) => {
                                const sno = (i + 1).toString().padStart(2, '0');
                                if (q.question === null) {
                                    $("#question_preview").append(`
                                        <div class="question mb-3">
                                            <p style="margin: 0; line-height: 1.8;">
                                                <strong>${sno}. </strong>
                                                dynamic question
                                                <span style="color: #555; margin-left: 15px;">
                                                    <strong>Topic:</strong> ${q.topic || "-"}
                                                </span>
                                                <span style="color: #555; margin-left: 15px;">
                                                    <strong>Subtopic:</strong> ${q.subtopic || "-"}
                                                </span>
                                            </p>
                                        </div>
                                    `);
                                } else {
                                    $("#question_preview").append(`
                                        <div class="question mb-3">
                                            <p style="margin: 0; line-height: 1.8;">
                                                <strong>${sno}. </strong>${q.question}
                                            </p>
                                        </div>
                                    `);
                                }
                            });
                        } else {
                            $("#question_preview").html("<p>No questions found.</p>");
                        }

                               
                        //         $("#question_preview").append(`
                                   
                        //             <div class="question mb-3">
                        //                 <p style="margin: 0; line-height: 2.0;">
                        //                     <strong>${sno}. </strong>${q.question || "dynamic question"}
                        //                 </p>
                        //             </div>
                        //         `);
                        //     });
                        // } else {
                        //     $("#question_preview").html("<p>No questions found.</p>");
                        // }
                    },
                    error: function (xhr, status, error) {
                        $("#question_preview").html("<p class='text-danger'>Failed to load questions.</p>");
                        console.error("Error fetching preview questions:", error);
                    },
                });
            } else {
                $("#question_preview").html("<p>No paper found for this test.</p>");
            }
        },
        error: function (xhr, status, error) {
            $("#question_preview").html("<p class='text-danger'>Failed to get paper ID.</p>");
            console.error("Error fetching paper_id:", error);
        },
    });
}

// Close modal
function close_paper_preview() {
    document.getElementById("overlay").style.display = "none";
}


function initTooltips() {
    const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]');
    tooltipTriggerList.forEach(el => {
        new bootstrap.Tooltip(el);
    });
}

function searchJDQuestions(input) {

    const keyword = input.value.toLowerCase().trim();
    const testId = input.dataset.testid;

    // Check Screening tabs (only exists for Screening test)
    const screeningTab = document.getElementById(`screeningTab_1_${testId}`);

    //  JD Screening – Basic
    if (screeningTab && screeningTab.classList.contains("active-screeningTab")) {
        const container = document.getElementById(`basicScreeningContainer_${testId}`);
        filterQuestions(container, keyword);
        return;
    }

    //  JD Knowledge / Coding / Interview
    const container = document.getElementById(
        `skillsAndTopicsAndSubtopicsContainer_${testId}`
    );
    filterQuestions(container, keyword);
}
function filterQuestions(container, keyword) {

    if (!container) return;

    const questions = container.querySelectorAll("li[id^='question_id_']");

    questions.forEach(li => {
        const text = li.innerText.toLowerCase();
        const questionBlock = li.closest(".customQuestionContainer");

        if (!questionBlock) return;

        questionBlock.style.display = text.includes(keyword) ? "" : "none";
    });
}
