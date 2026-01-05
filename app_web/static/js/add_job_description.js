var technologiesList = languages
var jdSelectedSkillsList = []
var jdSelectedSecondarySkillsList = [];

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

        // Filter the object keys based on the query
        const skillsList = Object.keys(technologiesList).filter(skill =>
            skill.toLowerCase().includes(query) // Match skill names (keys) with query
        );

        // Clear previous suggestions
        suggestionsBox.innerHTML = '';

        // Show suggestions or "Skill Not Found" if none match
        if (skillsList.length > 0) {
            let suggestionsHTML = '';

            // Loop through the filtered skills (keys) and build the HTML string
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

    // hide and unhide the empty skills container
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

    skillContainer.id = skillIteam.replace('.', '_');
    skillContainer.innerHTML = `
        <div class="skillTitle">${skillIteam}</div>
        <div id="removeSkill">
            &nbsp;&nbsp;&nbsp; 
            <i class="fas fa-times customremovecls" onclick="removeSkill('${skillIteam.replace('.', '_')}')"></i>
        </div>`;

    // creating dictionary to put in list
    var addNewSkill = {[skillIteam] : languages[skillIteam]}
    
    // Add to selected skills list
    jdSelectedSkillsList.push(addNewSkill);
    
    document.getElementById('skillsListMainContainer').appendChild(skillContainer);

    delete technologiesList[skillIteam];

    // hide and unhide the empty skills container
    emptySkillsContainer();
}

function removeSkill(rmSkill) {
    // Find the element to remove
    var rmElement = document.getElementById(rmSkill);

    var skillTitle = rmElement.querySelectorAll('.skillTitle')[0].innerText;

    if (rmElement) {
        // Remove the element from the DOM
        rmElement.remove();
        
        // adding the skill again to technologies list
        // dictionary   key            value
        technologiesList[skillTitle] = languages[skillTitle];
    }

    // Iterate over the jdSelectedSkillsList
    for (let skillCount = 0; skillCount < jdSelectedSkillsList.length; skillCount++) {
        const skillItem = jdSelectedSkillsList[skillCount];
        
        // Check if skillTitle exists in skillItem
        if (skillItem && skillItem.hasOwnProperty(skillTitle)) {
            delete skillItem[skillTitle];
        }
    }

    // Remove empty dictionaries from jdSelectedSkillsList
    jdSelectedSkillsList = jdSelectedSkillsList.filter(skillItem => Object.keys(skillItem).length > 0);

    jdSelectedSkillsList = jdSelectedSkillsList.filter(
        skillItem => !skillItem.hasOwnProperty(skillTitle)
    );


    // Hide and unhide the empty skills container
    emptySkillsContainer();
}


// Clear all input fields in JD
function resetJd(){
    // selectValidJd = false
    // libraryId = ''
    document.querySelectorAll("input").forEach(input => input.value = "");
    document.querySelectorAll("select").forEach(select => select.selectedIndex = 0);
    document.querySelectorAll("textarea").forEach(textarea => textarea.value = "");
    showSuccessMessage('Jd cleared');
}


// saving JD
document.getElementById('addJD').addEventListener('submit', function(event) {
    event.preventDefault(); // Prevent the default form submission

    // if (selectValidJd){ // verifying jd is selected or not selected
        
        const jdValues = {
            title: document.getElementById('jdTitle').value,
            // jdLibraryId : libraryId,
            jobDesc: document.getElementById('JobDescription').value,
            role: document.getElementById('jdRole').value,
            minExp: document.getElementById('min_experince').value,
            maxExp: document.getElementById('max_experince').value,
            budget: document.getElementById('jdBudget').value,
            noPositions: document.getElementById('jdNoPositions').value,
            workLocation: document.getElementById('jdWorkLocation').value,
            skills: jdSelectedSkillsList,
            secondarySkills: jdSelectedSecondarySkillsList,
            anySpecialNote: document.getElementById('JdanySpecialNotes').value,
            hiringmanager: document.getElementById('Hiring-Manager').value,
        };

        // Prepare data to be sent to the backend
        var final_data = {
            "data": JSON.stringify(jdValues),
            csrfmiddlewaretoken: CSRF_TOKEN,
        };
        try {
            $.post(CONFIG['portal'] + "/api/add-jd", final_data, function(res) {
                if (res.statusCode == 0) {
                    var newjdid = res.data['newJdId']
                    document.getElementById('validater').hidden = false;
                    setInterval(3000)
                    window.location.href = '/job-descriptions';
                }
            });
        } catch (error) {
            console.error('Failed to send data to backend:', error);
        }

    // }
    
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

    jdSelectedSecondarySkillsList =
        jdSelectedSecondarySkillsList.filter(x => !x[skillTitle]);

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