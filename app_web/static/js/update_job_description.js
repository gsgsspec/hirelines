var technologiesList = languages
var jdSelectedSkillsList = []

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
    
    if(skillsList){
        // var JDSkillsList = skillsList.split(',')
        
        jdSkillsSetOnBoard(skillsList)
        document.getElementById('jdSkillsContainer').hidden = false
    }

    if(checkjdstatus != 'I'){
        document.getElementById('jdStatus').checked = true
    }

}


// function jdSkillsSetOnBoard(skillList){

//     // Clean the string to make it valid JSON (replace single quotes with double quotes)
//     const validJsonStr = skillList.replace(/'/g, '"');

//     // Convert the string into a JavaScript array
//     const array = JSON.parse(validJsonStr);

//     console.log('array :: ',array);

//     for(var jdskill = 0; jdskill < array.length; jdskill++){
//         // selected jd skill 

//         console.log('key :: ',Object.keys(array[jdskill])[0],array[jdskill]);

//         selectedSkill(Object.keys(array[jdskill])[0])
//     }
// }



function jdSkillsSetOnBoard(skillList) {

    var newData = eval(skillList)

    for (var jdskill = 0; jdskill < newData.length; jdskill++) {

        selectedSkill(Object.keys(newData[jdskill])[0]);
    }

}




// document.addEventListener('DOMContentLoaded', function() {
//     const searchInput = document.getElementById('searchNewSkill');
//     const suggestionsBox = document.getElementById('suggestionsBox');

//     // Function to show suggestions based on the search input
//     function showSuggestions() {
//         const query = searchInput.value.trim().toLowerCase();

//         // Display prompt message if less than 3 characters are entered
//         if (query.length < 1) {
//             suggestionsBox.style.display = "none";
//             return;
//         }

//         // Filter the technologies list based on the query
//         const skillsList = technologiesList.filter(skill =>
//             skill.toLowerCase().includes(query) // Match skill names with query
//         );

//         // Clear previous suggestions
//         suggestionsBox.innerHTML = '';

//         // Show suggestions or "No job descriptions found" if none match
//         if (skillsList.length > 0) {
//             let suggestionsHTML = '';

//             // Loop through the filtered descriptions and build the HTML string
//             for (let i = 0; i < skillsList.length; i++) {
//                 const skill = skillsList[i];

//                 suggestionsHTML += `
//                     <div class="suggestion-item p-2 search_item" 
//                          style="cursor: pointer;" 
//                          onclick="selectedSkill('${skill}')">
//                         ${skill}
//                     </div>
//                 `;
//             }

//             // Insert the suggestions into the suggestions box
//             suggestionsBox.innerHTML = suggestionsHTML;
//         } else {
//             suggestionsBox.innerHTML = `<div class="p-2 text-muted">Skill Not Found</div>`;
//         }

//         // Display the suggestions box
//         suggestionsBox.style.display = "block";
//     }

//     // Trigger suggestions on input and focus
//     searchInput.addEventListener('input', showSuggestions);
//     searchInput.addEventListener('focus', showSuggestions);

//     // Hide suggestions on outside click
//     document.addEventListener('click', function(e) {
//         if (!searchInput.contains(e.target) && !suggestionsBox.contains(e.target)) {
//             suggestionsBox.style.display = "none";
//         }
//     });

//     // Add click event to select a suggestion
//     suggestionsBox.addEventListener('click', function(e) {
//         if (e.target.classList.contains('suggestion-item')) {
//             searchInput.value = e.target.textContent.trim();
//             searchInput.blur();
//             suggestionsBox.style.display = "none";
//             document.getElementById('searchNewSkill').value = '';
//             document.getElementById('searchNewSkill').focus()
//         }
//     });

//     // hide and unhide the empty skills container
//     emptySkillsContainer()

// });



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


// function selectedSkill(skillIteam) {
//     if (skillIteam) {
//         // Remove skill from technologies list
//         let index = technologiesList.indexOf(skillIteam.trim());
//         // if index is -1 thay means item was not in the list
//         if (index !== -1) {
//             technologiesList.splice(index, 1); // Remove the skill from technologies list

//             // Create the skill container div
//             var skillContainer = document.createElement('div');
//             skillContainer.className = 'skillIteamContainer';
//             skillContainer.id = skillIteam.trim().replace('.', '_');
//             skillContainer.innerHTML = `
//                 <div class="skillTitle">${skillIteam}</div>
//                 <div id="removeSkill">
//                     &nbsp;&nbsp;&nbsp; 
//                     <i class="fas fa-times customremovecls" onclick="removeSkill('${skillContainer.id}')"></i>
//                 </div>`;

//             jdSelectedSkillsList.push(skillIteam);

//             // Append the new skill container to the main container
//             document.getElementById('skillsListMainContainer').appendChild(skillContainer);
//         } else {
//             console.log('Cannot find the skill index value', index, skillIteam);
//         }
//     }

//     // Show or hide the empty skills container
//     emptySkillsContainer();
// }

// function selectedSkill(skillIteam) {
//     if (skillIteam) {
//         // Trim and check if the skill exists in the technologiesList dictionary
//         let skillKey = skillIteam.trim();
        
//         if (technologiesList.hasOwnProperty(skillKey)) {
//             // Remove the skill from the technologiesList dictionary
//             delete technologiesList[skillKey]; // Remove skill from dictionary

//             // Create the skill container div
//             var skillContainer = document.createElement('div');
//             skillContainer.className = 'skillIteamContainer';
//             skillContainer.id = skillKey.replace('.', '_');
//             skillContainer.innerHTML = `
//                 <div class="skillTitle">${skillKey}</div>
//                 <div id="removeSkill">
//                     &nbsp;&nbsp;&nbsp; 
//                     <i class="fas fa-times customremovecls" onclick="removeSkill('${skillContainer.id}')"></i>
//                 </div>`;

//             jdSelectedSkillsList.push(skillKey); // Add to selected skills list

//             // Append the new skill container to the main container
//             document.getElementById('skillsListMainContainer').appendChild(skillContainer);
//         } else {
//             console.log('Skill not found in the dictionary', skillKey);
//         }
//     }

//     // Show or hide the empty skills container
//     emptySkillsContainer();
// }


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
    
    // Add to selected skills list
    jdSelectedSkillsList.push(addNewSkill);
    
    document.getElementById('skillsListMainContainer').appendChild(skillContainer);

    delete technologiesList[skillIteam];

    // Remove the skill from the languages object (equivalent to removing from the technologiesList)
    // if (technologiesList.hasOwnProperty(skillIteam)) {
    //     delete technologiesList[skillIteam]; // Remove selected skill from languages object
    // }

    // hide and unhide the empty skills container
    emptySkillsContainer();
}



// function removeSkill(skillId) {
//     // Find the element to remove
//     var rmElement = document.getElementById(skillId);

//     if (rmElement) {
//         // Get the skill title
//         var skillTitle = rmElement.querySelector('.skillTitle').innerText;

//         // Remove the element from the DOM
//         rmElement.remove();

//         // Remove the skill from the selected skills list
//         var rmJdSkill = jdSelectedSkillsList.indexOf(skillTitle);
//         // if index is -1 thay means item was not in the list
//         if (rmJdSkill !== -1) {
//             // Remove the skill from the selected JD skills
//             jdSelectedSkillsList.splice(rmJdSkill, 1);

//             // Add the skill back to the technologies list
//             technologiesList.push(skillTitle);
//         }
//     } else {
//         console.error('Element with id not found:', skillId);
//     }

//     // Show or hide the empty skills container
//     emptySkillsContainer();

//     console.log('jdSelectedSkillsList :: ',jdSelectedSkillsList)
// }


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
        for (let skillCount = 0; skillCount < jdSelectedSkillsList.length; skillCount++) {
            const skillItem = jdSelectedSkillsList[skillCount];
            
            // Check if skillTitle exists in skillItem
            if (skillItem && skillItem.hasOwnProperty(skillTitle)) {
                delete skillItem[skillTitle];
            }
        }

    }

    // Remove empty dictionaries from jdSelectedSkillsList
    jdSelectedSkillsList = jdSelectedSkillsList.filter(skillItem => Object.keys(skillItem).length > 0);

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
        skills         : jdSelectedSkillsList,
        anySpecialNote : document.getElementById('JdanySpecialNotes').value,
        jobDescriptionStatus : jdStatus,
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

    const payload = {
        JdID: JdId,
        status: statusCode
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
                showSuccessMessage(successMsg);
                setInterval(5000)
                window.location.href = '/job-descriptions';

            } else {
                showFailureMessage("Status update failed");
            }
        }
    });
}