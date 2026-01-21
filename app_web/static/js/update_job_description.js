var technologiesList = languages
var jdSelectedSkillsList = []
var jdSelectedSecondarySkillsList = [];

addEventListener("DOMContentLoaded", function(){
    getJDData()
});


function getJDData(){

    const jdValues = {
        JdID : JdId,
    };
    
    // Prepare data to be sent to the backend
    var final_data = {
        "data":JSON.stringify(jdValues),
        csrfmiddlewaretoken: CSRF_TOKEN,
    };

    try {
        $.post(CONFIG['portal'] + "/api/update-jd-data", final_data, function (res) {
            console.log('res :: ',res);
            if (res.statusCode == 0){
                setDataInInputs(res)
            }
        })
    
    } catch (error) {
        console.error('Failed to get jd data :', error);
    }
}


function setDataInInputs(data){
    document.getElementById('JdTitle').value = data['data']['title']
    document.getElementById('JobDescription').value = data['data']['description']
    document.getElementById('jdRole').value = data['data']['role']
    document.getElementById('min_experince').value = data['data']['expmin']
    document.getElementById('max_experince').value = data['data']['expmax']
    document.getElementById('jdBudget').value = data['data']['budget']
    document.getElementById('jdNoPositions').value = data['data']['positions']
    document.getElementById('jdWorkLocation').value = data['data']['location']
    document.getElementById('JdanySpecialNotes').value = data['data']['skillnotes']
    var checkjdstatus = data['data']['status']
    var skillsList = data['data']['skillset']
    var secondarySkillsList = data['data']['secondaryskills']
    console.log("secondarySkillsList",secondarySkillsList);
    
    
    if(skillsList){
        // var JDSkillsList = skillsList.split(',')
        
        jdSkillsSetOnBoard(skillsList)
        document.getElementById('jdSkillsContainer').hidden = false
    }
    
    if(secondarySkillsList){
        // var JDSkillsList = skillsList.split(',')
        
        jdSecondarySkillSetOnBoard(secondarySkillsList)
        document.getElementById('jdSecondarySkillsContainer').hidden = false
    }

    if(checkjdstatus != 'I'){
        document.getElementById('jdStatus').checked = true
    }
   
    const hmElement = document.getElementById('Hiring-Manager');

    const hmValue = data['data']['hiring-manager'] || data['data']['hiringmanagerid'];

    console.log("Attempting to select Manager ID:", hmValue);

    if (hmValue && hmValue !== "None") {
        
        hmElement.value = String(hmValue);
        
       
        hmElement.dispatchEvent(new Event('change'));
    }

}


function jdSkillsSetOnBoard(skillList) {

    var newData = eval(skillList)

    for (var jdskill = 0; jdskill < newData.length; jdskill++) {

        selectedSkill(Object.keys(newData[jdskill])[0]);
    }

}

function jdSecondarySkillSetOnBoard(skillList) {

    var newData = eval(skillList)

    for (var jdskill = 0; jdskill < newData.length; jdskill++) {

        selectedSecondarySkill(Object.keys(newData[jdskill])[0]);
    }

}


document.addEventListener('DOMContentLoaded', function() {
    const searchInput = document.getElementById('searchNewSkill');
    const suggestionsBox = document.getElementById('suggestionsBox');

    // Function to show suggestions based on the search input
    function showSuggestions() {
        const query = searchInput.value.trim().toLowerCase();

        // Display prompt message if less than 1 character is entered
        if (query.length < 1) {
            suggestionsBox.style.display = "none";
            return;
        }

        // Filter the technologies list based on the query
        const skillsList = Object.keys(languages).filter(skill =>
            skill.toLowerCase().includes(query) // Match skill names with query from object keys
        );

        // Clear previous suggestions
        suggestionsBox.innerHTML = '';

        // Show suggestions or "No job descriptions found" if none match
        if (skillsList.length > 0) {
            let suggestionsHTML = '';

            // Loop through the filtered descriptions and build the HTML string
            for (let i = 0; i < skillsList.length; i++) {
                const skill = skillsList[i];

                suggestionsHTML += `
                    <div class="suggestion-item p-2 search_item" 
                         style="cursor: pointer;" 
                         onclick="selectedSkill('${skill}')">
                        ${skill}
                    </div>
                `;
            }

            // Insert the suggestions into the suggestions box
            suggestionsBox.innerHTML = suggestionsHTML;
        } else {
            suggestionsBox.innerHTML = `<div class="p-2 text-muted">Skill Not Found</div>`;
        }

        // Display the suggestions box
        suggestionsBox.style.display = "block";
    }

    // Trigger suggestions on input and focus
    searchInput.addEventListener('input', showSuggestions);
    searchInput.addEventListener('focus', showSuggestions);

    // Hide suggestions on outside click
    document.addEventListener('click', function(e) {
        if (!searchInput.contains(e.target) && !suggestionsBox.contains(e.target)) {
            suggestionsBox.style.display = "none";
        }
    });

    // Add click event to select a suggestion
    suggestionsBox.addEventListener('click', function(e) {
        if (e.target.classList.contains('suggestion-item')) {
            searchInput.value = e.target.textContent.trim();
            searchInput.blur();
            suggestionsBox.style.display = "none";
            document.getElementById('searchNewSkill').value = '';
            document.getElementById('searchNewSkill').focus()
        }
    });

    // Hide and unhide the empty skills container
    emptySkillsContainer();

});



// hide and unhide the empty skills container
function emptySkillsContainer(){
    var skillscontainer = document.getElementById('skillsListMainContainer')
    if(skillscontainer.childNodes.length == 1){
        document.getElementById('jdSkillsContainer').hidden = true
    }
    else{
        document.getElementById('jdSkillsContainer').hidden = false
    }
}


function selectedSkill(skillIteam) {
    // Create a new skill item container div
    var skillContainer = document.createElement('div');
    skillContainer.className = 'skillIteamContainer';

    console.log('skillIteam :: ',skillIteam);

    skillContainer.id = skillIteam.replace('.', '_');
    skillContainer.innerHTML = `
        <div class="skillTitle">${skillIteam}</div>
        <div id="removeSkill">
            &nbsp;&nbsp;&nbsp; 
            <i class="fas fa-times customremovecls" onclick="removeSkill('${skillIteam.replace('.', '_')}')"></i>
        </div>`;

    // creating dictionary to put in list
    var addNewSkill = {[skillIteam] : languages[skillIteam]}
    console.log("addNewSkill",addNewSkill);
    
    
    // Add to selected skills list
    jdSelectedSkillsList.push(addNewSkill);
    
    document.getElementById('skillsListMainContainer').appendChild(skillContainer);

    delete technologiesList[skillIteam];

    // hide and unhide the empty skills container
    emptySkillsContainer();
}


function removeSkill(skillId) {
    // Find the element to remove
    var rmElement = document.getElementById(skillId);

    if (rmElement) {
        // Get the skill title
        var skillTitle = rmElement.querySelector('.skillTitle').innerText;

        // Remove the element from the DOM
        rmElement.remove();

        // Add the skill back to the technologies list
        technologiesList[skillTitle] = languages[skillTitle];

        // Iterate over the jdSelectedSkillsList removing from the selected skillslist
        // for (let skillCount = 0; skillCount < jdSelectedSkillsList.length; skillCount++) {
        //     const skillItem = jdSelectedSkillsList[skillCount];
            
        //     // Check if skillTitle exists in skillItem
        //     if (skillItem && skillItem.hasOwnProperty(skillTitle)) {
        //         delete skillItem[skillTitle];
        //     }
        // }

        jdSelectedSkillsList = jdSelectedSkillsList.filter(
            skillItem => !skillItem.hasOwnProperty(skillTitle)
        );

        // Safety net (optional but good)
        jdSelectedSkillsList = jdSelectedSkillsList.filter(
            item => Object.keys(item).length > 0
        );

    }

    // Show or hide the empty skills container
    emptySkillsContainer();

    // Log the updated selected skills list
    console.log('jdSelectedSkillsList :: ', jdSelectedSkillsList);
}



function activeJDOrInactiveJd() {
    var statusLabel = document.getElementById('statusLabel');
    var jdStatus = document.getElementById('jdStatus');

    // Check if the checkbox is checked
    if (jdStatus.checked) {
        statusLabel.textContent = '( Active )';
    } else {
        statusLabel.textContent = '( Inactive )';
    }
}


document.getElementById('addJD').addEventListener('submit', function(event) {
    event.preventDefault(); // Prevent the default form submission
    var jdStatus
    var jdStatusElement = document.getElementById('jdStatus');
    if (jdStatusElement.checked) {
        jdStatus = 'D'
    } else {
        jdStatus = 'I'
    }


    // Gather data from the form
    const jdValues = {
        JdID         : JdId,
        title       : document.getElementById('JdTitle').value,
        jobDesc     : document.getElementById('JobDescription').value,
        role        : document.getElementById('jdRole').value,
        minExp      : document.getElementById('min_experince').value,
        maxExp      : document.getElementById('max_experince').value,
        budget      : document.getElementById('jdBudget').value,
        noPositions : document.getElementById('jdNoPositions').value,
        workLocation   : document.getElementById('jdWorkLocation').value,
        skills         : cleanSkills(jdSelectedSkillsList),
        secondarySkills: cleanSkills(jdSelectedSecondarySkillsList),
        anySpecialNote : document.getElementById('JdanySpecialNotes').value,
        jobDescriptionStatus : jdStatus,
        hiringmanager: document.getElementById('Hiring-Manager').value,
    };
    
    // Prepare data to be sent to the backend
    var final_data = {
        "data":JSON.stringify(jdValues),
        csrfmiddlewaretoken: CSRF_TOKEN,
    };

    try {
        $.post(CONFIG['portal'] + "/api/update-jd", final_data, function (res) {
            if (res.statusCode == 0){   
               document.getElementById('validater').hidden = false;
               setInterval(1000)
               window.location.href = '/job-descriptions';
            }
        })

    } catch (error) {
        console.error('Failed to send data to backend:', error);
    }
});


function updateJDStatus(statusCode, successMsg) {
    let comments = "";

    if (statusCode === 'R') {
        comments = document.getElementById("reviseComments")?.value.trim() || "";
    }

    const payload = {
        JdID: JdId,
        status: statusCode,
        comments: comments

    };

    $.ajax({
        url: CONFIG['portal'] + "/api/update-status",
        type: "POST",
        data: {
            data: JSON.stringify(payload),
            csrfmiddlewaretoken: CSRF_TOKEN
        },
        success: function (res) {
            if (res.statusCode === 0) {
                if (statusCode === 'R') {
                    $('#reviseModal').modal('hide');
                }
                showSuccessMessage(successMsg);
                setInterval(5000)
                window.location.href = '/job-descriptions';

            } else {
                showFailureMessage("Status update failed");
            }
        }
    });
}


$(document).on("click", "#assign-recruiters", function () {

    let selectedIds = [];

    $(".recruiter-checkbox:checked").each(function () {
        selectedIds.push($(this).val());
    });

    dataObjs = {
        "jdid": JdId,
        "recruiter_ids":selectedIds
    }

    var final_data = {
        "data":JSON.stringify(dataObjs),
        csrfmiddlewaretoken: CSRF_TOKEN,
    };

    try {
        $.post(CONFIG['portal'] + "/api/jd-recruiter-assign", final_data, function (res) {
            if (res.statusCode == 0){   

                Swal.fire({
                    position: 'center',
                    icon: 'success',
                    title: 'Recruiter assigned successfully',
                    showConfirmButton: false,
                    timer: 1500
                })
            }
        })

    } catch (error) {
        console.error('Failed to send data to backend:', error);
    }
});


document.addEventListener('DOMContentLoaded', function() {

    const searchInput = document.getElementById('searchSecondarySkill');
    const suggestionsBox = document.getElementById('secondarySuggestionsBox');

    function showSecondarySuggestions() {
        const query = searchInput.value.trim().toLowerCase();
        if (!query) {
            suggestionsBox.style.display = "none";
            return;
        }

        const skillsList = Object.keys(technologiesList).filter(skill =>
            skill.toLowerCase().includes(query)
        );

        suggestionsBox.innerHTML = "";

        suggestionsBox.innerHTML = skillsList.length
            ? skillsList.map(skill => `
                <div class="suggestion-item p-2 search_item"
                     style="cursor:pointer"
                     onclick="selectedSecondarySkill('${skill}')">
                    ${skill}
                </div>`).join("")
            : `<div class="p-2 text-muted">Skill Not Found</div>`;

        suggestionsBox.style.display = "block";
    }

    searchInput.addEventListener('input', showSecondarySuggestions);
    searchInput.addEventListener('focus', showSecondarySuggestions);

    document.addEventListener('click', function(e) {
        if (!searchInput.contains(e.target) && !suggestionsBox.contains(e.target)) {
            suggestionsBox.style.display = "none";
        }
    });

    // Add click event to select a suggestion
    suggestionsBox.addEventListener('click', function(e) {
        if (e.target.classList.contains('suggestion-item')) {
            searchInput.value = e.target.textContent.trim();
            searchInput.blur();
            suggestionsBox.style.display = "none";
            document.getElementById('searchSecondarySkill').value = '';
            document.getElementById('searchSecondarySkill').focus()
        }
    });

    emptySecondarySkillsContainer()
});


function selectedSecondarySkill(skillIteam) {

    var skillContainer = document.createElement('div');
    skillContainer.className = 'skillIteamContainer';
    skillContainer.id = "secondary_" + skillIteam.replace('.', '_');

    skillContainer.innerHTML = `
        <div class="skillTitle">${skillIteam}</div>
        <div>
            &nbsp;&nbsp;&nbsp; 
            <i class="fas fa-times customremovecls"
               onclick="removeSecondarySkill('${skillContainer.id}')"></i>
        </div>`;

    jdSelectedSecondarySkillsList.push({ [skillIteam]: languages[skillIteam] });

    document.getElementById('secondarySkillsListMainContainer')
            .appendChild(skillContainer);

    delete technologiesList[skillIteam]; // ⛔ prevents duplicate

    emptySecondarySkillsContainer()
}


function removeSecondarySkill(rmSkillId) {

    var rmElement = document.getElementById(rmSkillId);
    if (!rmElement) return;

    var skillTitle = rmElement.querySelector('.skillTitle').innerText;
    rmElement.remove();

    technologiesList[skillTitle] = languages[skillTitle];

    jdSelectedSecondarySkillsList = jdSelectedSecondarySkillsList.filter(item => !item.hasOwnProperty(skillTitle));

    emptySecondarySkillsContainer()
}


function emptySecondarySkillsContainer(){
    
    var skillscontainer = document.getElementById('secondarySkillsListMainContainer')
    
    if(skillscontainer.childNodes.length == 0){
        document.getElementById('jdSecondarySkillsContainer').hidden = true
    }
    else{
        document.getElementById('jdSecondarySkillsContainer').hidden = false
    }
}

const cleanSkills = (arr = []) =>
    arr.filter(obj =>
        obj &&
        Object.keys(obj).length > 0 &&
        Object.values(obj).every(v => v !== undefined && v !== "")
    );
    
// document.getElementById('Hiring-Manager').addEventListener('change', function() {
//     const submitBtn = document.getElementById('submitBtn');
//     // Enable button if a value is selected, otherwise disable it
//     submitBtn.disabled = (this.value === "");
// });

document.addEventListener('DOMContentLoaded', function() {
    const hiringManagerSelect = document.getElementById('Hiring-Manager');
    const submitBtn = document.getElementById('submitBtn');

    // 1. Define the validation logic
    function toggleButton() {
        submitBtn.disabled = (hiringManagerSelect.value === "");
    }

    // 2. Run it immediately on page load
    toggleButton();

    // 3. Run it whenever the dropdown changes
    hiringManagerSelect.addEventListener('change', toggleButton);
});


document.getElementById("publishBtn")?.addEventListener("click", function () {

    // Get selected job boards
    const selectedBoards = Array.from(
        document.querySelectorAll('input[name="job_boards"]:checked')
    ).map(cb => cb.value);

    const dataObjs = {
        "job_board_ids": selectedBoards,
        "jobid":JdId
    }

    const final_data = {
        data: JSON.stringify(dataObjs),
        csrfmiddlewaretoken: CSRF_TOKEN
    };
    console.log("dataObjs",dataObjs);

    $.post(CONFIG['portal'] + "/api/save-jb-job-boards", final_data, function (res) {

        if (res.statusCode === 0) {

            Swal.fire({
                icon: "success",
                title: "Published Successfully",
                text: "Job has been published to selected job boards.",
                timer: 2000,             
                showConfirmButton: false
            });

            const modalEl = document.getElementById("modalCenter");
            const modal = bootstrap.Modal.getInstance(modalEl);
            modal.hide();
        }

    }).fail(function () {
        Swal.fire({
            icon: "error",
            title: "Server Error",
            text: "Something went wrong. Please try again."
        });
    });

});